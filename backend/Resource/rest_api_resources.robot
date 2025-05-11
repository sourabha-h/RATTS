*** Settings ***
Library		RequestsLibrary
Library		Collections
Library		OperatingSystem

*** Variables ***
#${url}		https://api.restful-api.dev
#${id}		ff8081818ab4fa1c018ad1364bbb25ca
${return_code}		200
*** Keywords ***
list all objects test
    [Arguments]    ${base_url}     ${relative_url}    ${token}    ${json}
    Log To Console    ${base_url}${relative_url}
    Create Session     msession    ${base_url}
	${response}=	GET On Session    msession    ${relative_url}    json=${json}
    ${body}=    Convert To String    ${response.content}    
    Log To Console    ${body}
    ${status_code}=    Convert To String    ${response.status_code}
	Should Be Equal     ${status_code}    ${return_code}

Add object test
    [Arguments]    ${base_url}     ${relative_url}    ${token}    ${json}
    #${data} = 	Create Dictionary    color=pink    capacity=512 GB
    #${name} = 	Create Dictionary 	name=Samsung Galaxy s27 	data=&{data}
    ${header} = 	Create Dictionary    Content-Type=application/json   
    Create Session     msession    ${base_url}
	${response}=	POST On Session    msession    ${relative_url}    json=${json}    headers=${header}
    ${body}=    Convert To String    ${response.content}
    ${respdata}=    Evaluate    ${body}
    Log To Console    ${respdata}
    ${id}  Set Variable  ${respdata['id']}
    Log To Console    ${id}
    ${status_code}=    Convert To String    ${response.status_code}
	Should Be Equal     ${status_code}    ${return_code}
    #${respdata}=    Evaluate    json.loads(${response.json()})    json
    [Return]  ${id}
Get object test
    [Arguments]    ${base_url}     ${relative_url}    ${token}    ${json}    ${record_id}
    Create Session     msession    ${base_url}
	${response}=	GET On Session    msession    ${relative_url}/${record_id}
    ${body}=    Convert To String    ${response.content}
    Log To Console    ${body}
    ${status_code}=    Convert To String    ${response.status_code}
	Should Be Equal     ${status_code}    ${return_code}
    ${respdata}=    Evaluate    ${body}
    Log To Console    ${respdata}
    Log To Console   ID: ${respdata['id']}, NAME: ${respdata['name']}

Update object test
    [Arguments]    ${base_url}     ${relative_url}    ${token}    ${json}    ${record_id}
    ${header} = 	Create Dictionary    Content-Type=application/json   
    Create Session     msession    ${base_url}
	${response}=	PUT On Session    msession    ${relative_url}/${record_id}    json=${json}    headers=${header}
    ${status_code}=    Convert To String    ${response.status_code}
	Should Be Equal     ${status_code}    ${return_code}

Partially Update object test
    [Arguments]    ${base_url}     ${relative_url}    ${token}    ${json}    ${record_id}
    ${name} = 	Create Dictionary 	name=Samsung Galaxy s223
    ${header} = 	Create Dictionary    Content-Type=application/json   
    Create Session     msession    ${base_url}
	${response}=	PATCH On Session    msession    ${relative_url}/${record_id}    json=${json}    headers=${header}
    ${status_code}=    Convert To String    ${response.status_code}
	Should Be Equal     ${status_code}    ${return_code}

Delete object test
    [Arguments]    ${base_url}     ${relative_url}    ${token}    ${json}    ${record_id}
    ${header} = 	Create Dictionary    Content-Type=application/json   
    Create Session     msession    ${base_url}
	${response}=	DELETE On Session    msession    ${relative_url}/${record_id}  json=${json}  headers=${header}
    ${status_code}=    Convert To String    ${response.status_code}
	Should Be Equal     ${status_code}    ${return_code}