from robot.api import ResultVisitor
import re
def getrequest(self,msg):
        self.msg = msg
        start='Request:'
        end = 'Response:'
        cnt=msg.count(start)
        value=''
        if(cnt == 1):
            value=msg[msg.find(start)+len(start):msg.rfind(end)]
        elif(cnt > 1):
             msg=msg.replace(start,"*")
             msg=msg.replace(end,"*")
             res = msg.split("*")
             for i in range(len(res)): 
                 if(i%2!=0):  
                    value=value+"   Request:   "+res[i]
             #print(value)
        #value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\\', '&quot;');
        
        #value = msg.split("",1)
        
        return '<pre>'+value+'</pre>'
def getresp(self,msg):
        self.msg = msg
        #print(msg)
        #value = find_between(msg,"Response","</m")
        start='Response:'
        end = '</msg>'
        cnt=msg.count(start)
        value=''
        if(cnt == 1):
            value=msg[msg.find(start)+len(start):msg.rfind(end)]
        elif(cnt > 1):
             msg=msg.replace("Request:","*")
             msg=msg.replace("Response:","*")
             res = msg.split("*")
             for i in range(len(res)): 
                 if(i%2 ==0):  
                    value=value+"    Response:   "+res[i]
        #value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\\', '&quot;');
        #print(value)
        value=value.strip()
        return '<pre>'+value+'</pre>'

class TestResults(ResultVisitor):
   

    def __init__(self, soup, tbody, logname):
        self.soup = soup
        self.tbody = tbody
        self.log_name = logname


    
    def visit_test(self, test):
        table_tr = self.soup.new_tag('tr')
        self.tbody.insert(0, table_tr)

        table_td = self.soup.new_tag('td', style="word-wrap: break-word;max-width: 200px; white-space: normal")
        table_td.string = str(test.parent)
        table_tr.insert(0, table_td)

        table_td = self.soup.new_tag('td',
                                style="word-wrap: break-word;max-width: 250px; white-space: normal;cursor: pointer; text-decoration: underline; color:blue")
        table_td.string = str(test)
        table_td['onclick'] = "openInNewTab('%s%s%s','%s%s')" % (self.log_name, '#', test.id, '#', test.id)
        table_td['data-toggle'] = "tooltip"
        table_td['title'] = "Click to view '%s' logs" % test
        table_tr.insert(1, table_td)

        table_td = self.soup.new_tag('td')
        table_td.string = str(test.status)
        table_tr.insert(2, table_td)

        table_td = self.soup.new_tag('td')
        table_td.string = str(test.elapsedtime / float(1000))
        table_tr.insert(3, table_td)

        request= getrequest(self,test.message)
        #response= getresp(self,test.message)
        table_td = self.soup.new_tag('td')
        table_td.string = str(request)
        table_tr.insert(4, table_td)

        #request= getrequest(self,test.message)
        response= getresp(self,test.message)
        table_td = self.soup.new_tag('td')
        table_td.string = str(response)
        table_tr.insert(5, table_td)