import cx_Oracle
import csv
import Tests.csvtojson as csvtojson
from Tests.csvtojson import csvConvert
from Tests.csvtojson import inserttocsv
cx_Oracle.init_oracle_client(lib_dir=r"C:\\instantclient_21_12")
status='';
def db_query(fieldname,field_value):
    #print(fieldname)
    try: 
     
    # Type 1 Connection
    # pass the direct connection string for connection
        con = cx_Oracle.connect(user="pin_1", password="c1g2b3u4",
                               dsn="pp-brm-db-scan.dhiraagu.com.mv:1521/BRMUAT",
                               encoding="UTF-8")
           
           
        c = con.cursor()
        table_name=fieldname.split('.')[0]
        field_name=fieldname.split('.')[1]
        #print(table_name)
        #print(field_name)
        sql = "select count(*) from "+table_name+" where "+field_name+"="+"'"+field_value+"'"
        #print(sql)
       
        row=c.execute(sql)
        print(sql,(field_value,))
        for row in c:
            row[0] 
            print (row[0])
        if (row[0] > 0):
            
            return sql,"SUCCESS"
        else:
            return sql,"FAILURE"
      
    except cx_Oracle.DatabaseError as e:
        print("There is a problem with Oracle", e)
        #return "There is a problem with Oracle"
        return "FAILURE"
	    
        c.close()
        con.close()
        #return status

#st =db_query('PAYMENT_RECEIPT_T.RECEIPT_NO','P-5031732')
#print(st)