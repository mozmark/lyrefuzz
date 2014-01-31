import string
from string import Template

def build_description(details):
    return string.join(["<!-- %s: %s -->" % (item, value) for item, value in details],'\n')


events = [evt.rstrip() for evt in open('events.txt','r').readlines()]
sources = [src.rstrip() for src in open('sources.txt','r').readlines()]
sinks = [snk.rstrip() for snk in open('sinks.txt','r').readlines()]
filters = [fltr.rstrip() for fltr in open('filters.txt','r').readlines()]

template = Template(open('case_gen_template.html').read())

count = 0

for event_line in events:
    node, event_detail = event_line.split(':',1)
    event, event_desc = event_detail.split('//',1)

    for source_line in sources:
        source, source_desc = source_line.rsplit('//',1)
        for sink_line in sinks:
            sink, sink_desc = sink_line.rsplit('//',1)
            for filter_line in filters:
                filtr, filter_desc = filter_line.rsplit('//',1)
                f = open('generated/{:0>5}'.format(str(count))+'.html','w')
                descriptions = [
                        ('source', source_desc),
                        ('sink', sink_desc),
                        ('filter', filter_desc),
                        ('event', event_desc)
                        ];
                test = template.substitute(
                        {'source':source,
                            'sink':sink,
                            'event_hook':'hookEvent(\''+node+'\',\''+event+'\');',
                            'description': build_description(descriptions),
                            'title':'there will be a title here',
                            'filter':filtr
                            })
                count = count + 1
                f.write(test)
                f.close()
