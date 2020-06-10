from urllib.parse import urlencode
import urllib3
import os
import requests
import json

TARGET_DB = "userDB"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded, application/sparql-query, text/turtle',
    'Accept': 'text/turtle, application/rdf+xml, application/n-triples, application/trig, application/n-quads, '
              'text/n3, application/trix, application/ld+json, '  # application/sparql-results+xml, '
              'application/sparql-results+json, application/x-binary-rdf-results-table, text/boolean, text/csv, '
              'text/tsv, text/tab-separated-values '
}


def QueryToUserKB(query: str):
    server = "http://kbox.kaist.ac.kr:5820/%s/" % TARGET_DB
    values = urlencode({"query": query})
    # http = urllib3.PoolManager()
    url = server + 'query?' + values
    r = requests.get(url, headers=headers)
    # r = http.request('GET', url, headers=headers)
    request = r.json()

    return request


def QueryToMasterKB(query):
    server = 'http://kbox.kaist.ac.kr:5820/myDB/'

    values = urlencode({'query': query})
    http = urllib3.PoolManager()

    url = server + 'query?' + values
    r = http.request('GET', url, headers=headers)
    result = json.loads(r.data.decode('UTF-8'))

    return result


def InsertKnowledgeToUserKB(user_name: str, triple):
    def converter(s, p, o):
        return "\t".join(
            ["<" + s + ">", "<" + p + ">", "<" + o + ">", "."])

    fname = user_name + ".ttl"
    f = open(fname, "a+", encoding="utf-8")
    print(triple)
    for line in map(lambda x: converter(*x), triple):
        f.write(line + "\n")
    f.close()
    code = os.system("docker cp %s stardog_:/root/flagship/%s/%s" % (fname, user_name, fname))
    code |= os.system(
        """docker exec stardog_ /root/stardog/bin/stardog vcs commit --add /root/flagship/%s/%s -m 'user %s commited %s' -g "http://kbox.kaist.ac.kr/username/%s" %s""" % (
            user_name, fname, user_name, fname, user_name, TARGET_DB))
    # os.remove(fname)
    return True

