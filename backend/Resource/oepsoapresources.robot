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
Library    ../Tests/oep_validate.py
#Library    RPA.Windows
Variables          LocalConfig.yaml
*** Variables ***
${oep_base_url}            ${OEP_SOAP_BASE_URL}     
${oep_channel_url}         ${OEP_SOAP_CHNL_URL}    



*** Keywords ***

Check soap call 
    [Arguments]    ${jsondt}    ${template_name}    ${opcodename}   ${key}    
    ${arg}    Set variable     oep
    Generate Request     ${Templatename}     ${key}     ${arg}
    Call Soap Method    
   
Call Soap Method
       
        create session  soapsession    ${oep_base_url}     disable_warnings=1
        
    #Set a request variable
        ${SOAP_XML}=    Get File    Data/Input/oepsoapRequestXmls${/}oepsoaprequest.xml
       
    #Create Request Headers
        Set Test Message    Request:${\n}${SOAP_XML}${\n}    append=${True}
        ${request_header}=    create dictionary    Content-Type=text/xml; charset=utf-8   User-Agent=Apache-HttpClient/4.1.1

    #Send the XML request body to format
        
        ${SAVE_Response}=    POST On Session    soapsession    ${oep_channel_url}    headers=${request_header}    data=${SOAP_XML}
        ${xml_response}      Set Variable     ${SAVE_Response.content}        
        ${status}=    Get Status Code    ${xml_response}      
        Log To Console    StatusCode: ${status}
        Log To Console  ${status}
        ${success}     Should Not Be Empty      ${status}
        Log To Console  ${success}
        IF  ${status} == 00
            Log To Console  SUCCESS
        
        ELSE
            ${status_desc}=    Get Status Description    ${xml_response}   
            Log To Console    ${status_desc}
                 
            fail    (${status_desc} )
        
        END
        Set Test Message     Response:${\n}${xml_response}${\n}    append=${True}
        #[Return]    ${status}


