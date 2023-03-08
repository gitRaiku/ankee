#!/bin/python

from lxml import etree
import socket
import os
import traceback
import requests

def send_parsed_entries(csock, pe):
    l = bytearray()
    l.append((len(pe) & 0xFF00) >> 8)
    l.append((len(pe) & 0x00FF)     )

    for i in pe:
        l.append(len(i['t']))
        for j in i['t']:
            cs = j.encode('utf-8')
            l.append(len(cs))
            for x in cs:
                l.append(x)

        l.append(len(i['r']))
        for j in i['r']:
            cs = j.encode('utf-8')
            l.append(len(cs))
            for x in cs:
                l.append(x)

        l.append(len(i['m']))
        for j in i['m']:
            l.append(len(j['t']))
            for x in j['t']:
                cs = x.encode('utf-8')
                l.append(len(cs))
                for x in cs:
                    l.append(x)

            l.append(len(j['p']))
            for x in j['p']:
                cs = x.encode('utf-8')
                l.append(len(cs))
                for x in cs:
                    l.append(x)

    csock.send(l)


def fix(a):
    nn = 0
    ad = 0
    r = []
    for x in a:
        match x:
            case "nouns which may take the genitive case particle 'no'":
                r.append("Noun (takes の)")
                nn = 1
            case "noun (common) (futsuumeishi)":
                r.append("Noun")
            case "adverb taking the 'to' particle":
                r.append("Adverb (takes と)")
                ad = 1
            case "adverb (fukushi)":
                r.append("Adverb")
            case "noun, used as a prefix":
                r.append("Noun (prefix)")
            case "noun, used as a suffix":
                r.append("Noun (suffix)")
            case "noun or verb acting prenominally":
                r.append("Noun (acting prenom)")
            case "adverbial noun (fukushitekimeishi)":
                r.append("Noun (adv)")
            case "proper noun":
                r.append("Noun (proper)")
            case "noun (temporal) (jisoumeishi)":
                r.append("Noun (temporal)")
            case "adjective (keiyoushi)" | "adjective (keiyoushi) - yoi/ii class":
                r.append("Adjective")
            case "'kari' adjective (archaic)":
                r.append("Kuri adjective")
            case "'ku' adjective (archaic)":
                r.append("Ku adjective")
            case "'shiku' adjective (archaic)":
                r.append("Shiku adjective")
            case "'taru' adjective":
                r.append("Taru adj")
                ad = 1;
            case "archaic/formal form of na-adjective":
                r.append("Archaic na-adjective")
            case "pre-noun adjectival (rentaishi)":
                r.append("Pre noun adj")
            case "auxiliary":
                r.append("Aux")
            case "auxiliary adjective":
                r.append("Aux adj")
            case "auxiliary verb":
                r.append("Aux verb")
            case "conjunction":
                r.append("Conj")
            case "copula":
                r.append("Copula")
            case "counter":
                r.append("Counter")
            case "expressions (phrases, clauses, etc.)":
                r.append("Expression")
            case "interjection (kandoushi)":
                r.append("Interj")
            case "numeric":
                r.append("Numeric")
            case "pronoun":
                r.append("Pronoun")
            case "prefix":
                r.append("Prefix")
            case "particle":
                r.append("Particle")
            case "suffix":
                r.append("Suffix")
            case _:
                r.append(x)

    
    if nn:
        while True:
            try:
                r.remove("Noun")
            except:
                break
    
    if ad:
        while True:
            try:
                r.remove("Adverb")
            except:
                break

    return r

def gint(l, s):
    r = []
    for i in range(0, l):
        r.append((s[2 * i], s[2 * i + 1]))
    return r
        

def main():
    spath = '/tmp/ankeed.sock'
    if os.path.exists(spath):
        os.remove(spath)

    tree = etree.parse('JMdict_e.xml')
    print('Done reading!')

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(spath)
    server.listen()
    try:
        while True:
            (cs, addr) = server.accept()
            print(f'Got connection fron {addr}')
            while True:
                l = 0
                try: 
                    print('Waiting')
                    r = cs.recv(3)
                    l = r[0] << 8 | r[1]
                    if l == 0:
                        break
                except:
                    break
                if r[2] == 0:
                    text = cs.recv(l).decode("utf-8").replace('\x00', '')
                    print(f'Got {text}')

                    es = []
                    for x in tree.findall(f"//entry/k_ele[keb='{text}']"): # TODO: Xpath 'or' what the fuck
                        par = x.getparent()
                        if par not in es:
                            es.append(par)

                    for x in tree.findall(f"//entry/r_ele[reb='{text}']"): # TODO: Xpath 'or' what the fuck
                        par = x.getparent()
                        if par not in es:
                            es.append(par)

                    pe = []
                    for s in es:
                        st = ''
                        entry = {'t': [], 'r': [], 'm': []}
                        # print(etree.tostring(s, pretty_print=False).decode('utf-8'))
                        for x in s.findall('.//k_ele/keb'):
                            entry['t'].append(x.text)
                        for x in s.findall('.//r_ele/reb'):
                            entry['r'].append(x.text)
                        for x in s.findall('.//sense'):
                            meaning = {'t': [], 'p': []}
                            for y in x.findall('.//pos'):
                                meaning['p'].append(y.text)
                            for y in x.findall('.//gloss'):
                                meaning['t'].append(y.text)
                            meaning['t'][0] = meaning['t'][0].capitalize()
                            meaning['p'] = fix(meaning['p'])
                            entry['m'].append(meaning)
                        pe.append(entry)
                    send_parsed_entries(cs, pe)
                else:
                    text = cs.recv(l).decode("utf-8").replace('\x00', '')
                    print(f'Recv {l}: {text}');
                    tll = cs.recv(2)
                    tl = tll[0] << 8 | tll[1]
                    ot = cs.recv(tl).decode("utf-8").replace('\x00', '')
                    print(f'And got {tl}:{ot}');
                    dot = ot.split('\n')
                    l = int.from_bytes(cs.recv(1), byteorder='big')
                    ints = gint(l, cs.recv(l * 2))
                    print(f'With {l}: {ints}');

                    al = int.from_bytes(cs.recv(1), byteorder='big')
                    at = cs.recv(al).decode("utf-8").replace('\x00', '')
                    print(f'Apath {al}: {at}')

                    cd = 0
                    for i in range(len(ints)):
                        adds = f'<b>{dot[i].split("[")[0].split("/")[0]}</b>'
                        text = f'{text[0:ints[i][0] + cd]}{adds}{text[ints[i][0] + ints[i][1] + cd:-1]}'
                        cd += len(adds) - ints[i][1]

                    fname = at.split("/")[-1]
                    print(text)
                    s = f'{{\
"action": "guiAddCards",\
"version": 6,\
"params": {{\
"note": {{\
"deckName": "Sentence Mining",\
"modelName": "SentenceMining",\
"fields": {{\
"Sentence": "{text}",\
"Words": "{ot}",\
"Audio": ""\
}},\
"options": {{\
"allowDuplicate": false,\
"duplicateScope": "deck",\
"duplicateScopeOptions": {{\
"deckName": "Sentence Mining",\
"checkChildren": false,\
"checkAllModels": false\
}}\
}},\
"tags": [\
"audio"\
],\
"audio": [{{\
"filename": "{fname}",\
"path": "{at}",\
"fields": [\
"Audio"\
]\
}}]\
}}\
}}\
}}'.encode('utf-8')
                    print(s)
                    print(requests.post('http://localhost:8765', s))

            cs.close()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        pass
    server.close()
    os.remove(spath)

if __name__ == '__main__':
    main()
