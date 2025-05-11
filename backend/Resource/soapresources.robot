*** Settings ***
Library     RequestsLibrary
Library     Collections
Library     SeleniumLibrary
Library     String
Library     XML     
Library    SoapLibrary
Library    BuiltIn
Library    Process
Library    OperatingSystem
Library    ../Tests/soaprequestgeneration.py
Library    JSONLibrary
Variables          LocalConfig.yaml
*** Variables ***
${base_url}            ${SOAP_BASE_URL}     
${channel_url}         ${SOAP_CHNL_URL}  


*** Keywords ***

Check soap call 
    [Arguments]    ${jsondt}    ${template_name}    ${opcodename}   ${key}   
    Generate Request     ${Templatename}     ${key}    ""
    Call Soap Method     
   
Call Soap Method
        create session  soapsession    ${base_url}     disable_warnings=1
        
    #Set a request variable
        ${SOAP_XML}=    Get File    Data/Input/soapRequestXmls${/}soaprequest.xml
    #Create Request Headers
        Set Test Message    Request:${\n}${SOAP_XML}${\n}    append=${True}
        ${request_header}=    create dictionary    Content-Type=text/xml; charset=utf-8   User-Agent=Apache-HttpClient/4.1.1

    #Send the XML request body to format
        ${SAVE_Response}=    POST On Session    soapsession    ${channel_url}    headers=${request_header}    data=${SOAP_XML}
        ${xml_response}      Set Variable    echo ${SAVE_Response.content}
        ${xml_response}    Replace String    ${xml_response}    lt;    <
        ${xml_response}    Replace String    ${xml_response}    gt;    >
        ${xml_response}    Remove String    ${xml_response}     &    echo <?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><ns2:opcodeResponse xmlns:ns2="http://xmlns.oracle.com/BRM/schemas/BusinessOpcodes/"><opcodeResponse>    </opcodeResponse></ns2:opcodeResponse></S:Body></S:Envelope>
        ${xml_response}    Strip String       ${xml_response} 
    #Log Response and Status Code Details
        log to console    ${SAVE_Response.status_code}
        log    ${SAVE_Response.headers}
        log    ${SAVE_Response.content}
        log    ${xml_response}
        ${xml}=    Parse XML  ${xml_response}    
        ${elements}=    Get Element   ${xml}    STATUS
        ${status}=    Get Element Text    ${elements}
        Log To Console  ${status}
        ${success}     Should Not Be Empty      ${status}
        Log To Console  ${success}
        IF  ${status} == 0
            Log To Console  SUCCESS
        
        ELSE
            ${elements}=    Get Element   ${xml}    ERROR_DESCR
                ${error_descr}=    Get Element Text    ${elements}
                 
                 Log To Console    ${error_descr}
                 
                 fail    (${error_descr} )
        
        END
        Set Test Message     Response:${\n}${xml_response}${\n}    append=${True}
        #[Return]    ${status}
   
