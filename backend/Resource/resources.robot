*** Settings ****
Documentation          Requesting Opcode inputflist and  get the response
Library    SSHLibrary
Library    JSONLibrary
Library    Process
Library    OperatingSystem
Library    ../Tests/opcodegeneration.py
Library    Collections
#Library    DynamicTestCase.py
Library    re
Library    String
Library    ../Tests/getdata.py
Library    ../Tests/csvtojson.py
Library    ../Tests/runner_validate.py
Variables          LocalConfig.yaml

#Library    ../Tests/billing_python.py


*** Variables  ***
${HOST}         ${BRM_HOST}
${USERNAME}     ${BRM_USER}
${PASSWORD}     ${BRM_PWD}
${TESTFOLDER}   ${TEST}
${PVTCOMMAND}   pin_virtual_time -m2 ${PVT}
${PVT_FLAG}     ${FLAG}

*** Keywords ***
Open Connection And Log In
   Open Connection     ${HOST}
   SSHLibrary.Login               ${USERNAME}        ${PASSWORD}

Generate Opcode in loop
    [Arguments]    ${template}    ${key}    ${opcodename}
    Generate Opcode    ${template}   ${key}    ${opcodename}
    ${filename}=    Set Variable    ${opcodename}_${key}.txt
    Saving Opcode File To Remote Location and Executing Opcode    ${filename}   ${opcodename}   ${key}

Saving Opcode File To Remote Location and Executing Opcode
    [Arguments]    ${filename}      ${opcodename}   ${key}
    ${contents}=    OperatingSystem.Get File    Data/Input/generatedopcode${/}${filename}
    #Log    ${contents}
    Set Test Message    Request:${\n}${contents}${\n}    append=${True}
    ${uploadedfile}=   Put File   Data/Input/generatedopcode/${filename}    ${TESTFOLDER}/opcoderequest.txt     mode=0644    newline=LF
    ${output}=         Execute Command   cd ${TESTFOLDER};testnap opcoderequest.txt; 
    #Log    ${output} 
	Create File      Data/output/${filename}      ${output}
    Format Data      Data/output/${filename}
    Log    ${opcodename}
    Log To Console      "This is message from print, ${opcodename}";
    Set Test Message    Response:${\n}${output}${\n}    append=${True}
    #${success}     Should Not Be Empty      ${status}
    #Log To Console  ${success}
    ${status}=  runner_validate.Runner Validate     ${opcodename}   ${key}
    Log     ${status}
    IF  ${status}== 1 
        Log To Console      "This is the message from status condition clear";
        Run keyword  fail 
        #Process timed out
    
    END	 

Get Data From Opcode
    [Arguments]    ${opcode}    
    ${contents}=    OperatingSystem.Get File    Data/Input/generatedopcode${/}${opcode}
    #Log    ${contents}
    Set Test Message    Request:${\n}${contents}${\n}    append=${True}
    ${uploadedfile}=   Put File   Data/Input/generatedopcode/${opcode}   ${TESTFOLDER}/opcoderequest.txt      mode=0644    newline=LF
    ${output}=         Execute Command   cd ${TESTFOLDER};testnap opcoderequest.txt; 
    Set Test Message    Response:${\n}${output}${\n}    append=${True}
    Create File      Data/Input/formattedData/${opcode}      ${output}  
    Format Data    Data/Input/formattedData/${opcode}

Get Data From Opcode In Loop
    [Arguments]    ${opcode}     ${obj}  
    ${length}=    Get Length    ${obj}
    Log To Console      "This is the loop length for billinfo, ${length}";
    FOR    ${index}    IN RANGE    ${length}
        ${i}=    Evaluate    ${index}+1
        ${contents}=    OperatingSystem.Get File    Data/Input/generatedopcode${/}${opcode}_${i}.txt
        #Log    ${contents}
        Set Test Message    Request:${\n}${contents}${\n}    append=${True}
        ${uploadedfile}=   Put File   Data/Input/generatedopcode/${opcode}_${i}.txt   ${TESTFOLDER}/opcoderequest.txt      mode=0644    newline=LF
        ${output}=         Execute Command   cd ${TESTFOLDER};testnap opcoderequest.txt; 
        Set Test Message    Response:${\n}${output}${\n}    append=${True}
        Create File      Data/Input/formattedData/${opcode}_${i}.txt      ${output}  
        Format Data    Data/Input/formattedData/${opcode}_${i}.txt
    END

Get Data From File
    [Arguments]    ${filenames}     ${params}    ${csv_path}     ${objdata}
    @{lst}=    Create List
    &{dct}=    Create Dictionary
    @{datalst}=    Create List
    &{paramvalues}=    Create Dictionary
    &{data}=    Create Dictionary
    FOR    ${param}    IN    @{params}
        ${paramstr}=    Get Substring    ${param}    0    -1
        ${digit}=    Get Substring    ${param}       -1
        Log    ${paramstr}
        Log    ${digit}
        IF    @{lst}==@{EMPTY}
            Append To List    ${lst}    ${digit}
        ELSE
            ${cnt}=    Get Match Count    ${lst}    ${digit}
            IF    ${cnt}==0
                Append To List    ${lst}    ${digit}
                        
            END
        END
        Log    ${lst}
        FOR    ${ele}    IN    @{lst}
            IF   ${ele}==${digit}
                ${len}=    Get Length    ${dct}
                IF    ${len}!=0
                    ${keys}=    Get Dictionary Keys    ${dct}
                    Log    ${keys}
                    IF    '${ele}' in ${keys}
                    
                        @{datalst}=     Get From Dictionary       ${dct}    ${ele}  
                    ELSE
                        @{datalst}=    Create List
                    END                
                ELSE
                    @{datalst}=    Create List
                END   
                Log    ${datalst}
                Append To List    ${datalst}    ${paramstr}
                Set To Dictionary    ${dct}    ${ele}      ${datalst}
            
            END
            
        END
        Log    ${dct}
    END
    FOR    ${pd}    IN    ${lst}
        FOR    ${el}    IN    @{pd}
            IF    ${el}>=1 
                ${j}=  Evaluate      ${el}-1
                ${opcode}=   Set Variable      ${filenames}[${j}]
                Log    ${opcode}
                ${lst1}=     Get From Dictionary    ${dct}    ${el}
                ${paramvalues}=    Get Data    Data/Input/formattedData/${opcode}    ${lst1}
                Log    ${paramvalues}
            ELSE
                ${lst2}=    Get From Dictionary    ${dct}    0
                FOR    ${lst}    IN    ${lst2}
                    FOR    ${item}    IN    @{lst}
                        ${value}=    Get From Dictionary    ${objdata}[1]    ${item}
                        #Append To List    ${data}    ${value}
                        Set To Dictionary    ${paramvalues}    ${item}    ${value}
                        
                    END

                END
                Log    ${paramvalues}
            END
            ${data}=    Merge Dictionaries    ${data}    ${paramvalues}    
        END
    END
    Set To Dictionary    ${data}    no     1
    log     ${data}
    Insert To Csv    ${csv_path}    ${data}


Set pvt date for billing
    Log To Console      "CHANGING PVT FILE";
    IF  '${PVT_FLAG}' == 'YES'
        
        ${output}=         Execute Command   cd ${TESTFOLDER};pin_virtual_time;
        Log To Console   "Existing Pin Virtual time is ${output}";
         
    ELSE
        Log To Console     "Change Pin Virtual time ";
        ${output}=         Execute Command   cd ${TESTFOLDER};${PVTCOMMAND}; 
    END
