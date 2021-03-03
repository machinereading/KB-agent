KB_AGENT_PATH = "/home/ybjeong/project/KB-agent/"

dialogDBHost = '143.248.135.146'
dialogDBPort = 3142
dialogDBUserName = 'flagship'
dialogDBPassword = 'kbagent'
dialogDBDatabase = 'dialogDB'
dialogDBCharset = 'utf8'


HOME_DIRECTORY = "/root/flagship/"
DOCKER_EXEC_PREFIX = "docker exec stardog_"

TARGET_DB = "userDB"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded, application/sparql-query, text/turtle',
    'Accept': 'text/turtle, application/rdf+xml, application/n-triples, application/trig, application/n-quads, '
              'text/n3, application/trix, application/ld+json, '  # application/sparql-results+xml, '
              'application/sparql-results+json, application/x-binary-rdf-results-table, text/boolean, text/csv, '
              'text/tsv, text/tab-separated-values '
}
