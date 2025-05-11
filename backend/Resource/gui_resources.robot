*** Settings ***
Library    SeleniumLibrary
Library    BuiltIn
#Library    RPA.Windows
#Library    RPA.JavaAccessBridge
Library    Collections
#Library    RPA.RobotLogListener
Library    OperatingSystem
Variables          LocalConfig.yaml
#Library    YAMLLibrary
Library    String
Library    Process
#Library    AutoItLibrary


*** Variables ***
${gui}     ${GUI_URL}
${SCREENSHOT_DIR}      D:\bluerise_testing\RATTS\backend\Output\Metrics\gui_screenshots
*** Keywords ***
Open Application
    Set Screenshot Directory    ${SCREENSHOT_DIR}
    Open Browser    ${gui}    Chrome
    Sleep    1s  
    Set Selenium Timeout    10
    # Wait for browser to launch
    #Run Process    python    -c    import pyautogui; pyautogui.hotkey('alt', 'tab')
    #AutoIt Set Option    WinTitleMatchMode    2  # Partial title matching
    #AutoIt WinActivate    Chrome  # Bring Chrome browser to foreground

    # Maximize the browser window
    Maximize Browser Window   
    ${dynamic_title}=    Get Title
    Log To Console    ${dynamic_title}
    Title Should Be    ${dynamic_title}

Page Action
    [Arguments]    ${str_objdata}     ${template_name}    ${url}
    ${objdata}=    Evaluate    json.loads(r'''${str_objdata}''')    json
    #${json_str}=    Evaluate    json.dumps(${dict_objdata})    json
    #${objdata}=    Evaluate    json.loads(${json_str})    json
    Log To Console    Type of objdata: ${objdata.__class__.__name__}
    Log To Console    ${objdata}
    
    ${yaml_content}=    Get File    Data/Templates/guitemplates/${template_name}
      # Log the YAML and JSON data
    Log To Console    --- YAML Data ---
    Log To Console    ${yaml_content}
    @{result}    Convert Template To Lists    ${yaml_content}
    Log To Console    --- YAML List ---
    Log To Console     ${result}
    Log To Console    --- JSON Data ---
    Log To Console     ${objdata}
    Sleep    1s
    ${val_url}    Run Keyword And Return Status    Should Contain    ${url}    index
    IF    ${val_url}
        Go To    ${gui}${url}
        # Zoom to 75% using JavaScript
        Execute JavaScript    document.body.style.zoom='75%';
        Sleep    1s        
    END
    
    FOR    ${item}    IN    @{result}
            # Zoom to 75% using JavaScript
            Execute JavaScript    document.body.style.zoom='75%';
            ${type}    Set Variable    ${item['type']}
            ${str_text}    Run Keyword And Return Status    Should Contain    ${type}    text
            IF  ${str_text} 
                
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                    Log To Console    ${spec_var}
                   
                    Input Text    ${item['selector']}:${spec_var}     ${objdata["${spec_var}"]}             
                END
                Sleep    1s
                CONTINUE
            END
             ${str_number}    Run Keyword And Return Status    Should Contain    ${type}    number
            IF  ${str_number} 
                
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                    Log To Console    ${spec_var}
                    Input Text    ${item['selector']}:${spec_var}     ${objdata["${spec_var}"]}             
                END
                Sleep    1s
                CONTINUE
            END
            ${str_file}    Run Keyword And Return Status    Should Contain    ${type}    file
            IF  ${str_file} 
                
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                    Log To Console    ${spec_var}
                    IF    ${objdata["${spec_var}]} != ""
                       Input Text    ${item['selector']}:${spec_var}     ${objdata["${spec_var}"]}                    
                    END
                                 
                END
                Sleep    1s
                CONTINUE
            END
              ${str_text}    Run Keyword And Return Status    Should Contain    ${type}    textarea
            IF  ${str_text} 
                
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                    Log To Console    ${spec_var}
                    Input Text    xpath=//textarea[@${item['selector']}='${spec_var}']    ${EMPTY}
                    Input Text    xpath=//textarea[@${item['selector']}='${spec_var}']    ${objdata["${spec_var}"]}         
                END
                Sleep    1s
                CONTINUE
            END
            ${str_text}    Run Keyword And Return Status    Should Contain    ${type}    password
            IF  ${str_text} 
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                    Log To Console    ${spec_var}
                    Input Text    ${item['selector']}:${spec_var}     ${objdata["${spec_var}"]}
                                 
                END
                Sleep    1s
                CONTINUE
            END
                ${str_text}    Run Keyword And Return Status    Should Contain    ${type}    alert
            IF  ${str_text} 
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                    Log To Console    ${spec_var}
                    ${alert_text}=    Handle Alert    action=ACCEPT
                    Should Contain    ${alert_text}    ${objdata["${spec_var}"]}
                                 
                END
                Sleep    1s
                CONTINUE
            END
            ${str_select}    Run Keyword And Return Status    Should Contain    ${type}   select 
            IF    ${str_select}
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}   
                    ${value}    Run Keyword And Return Status    Should Contain    ${item['tag']}    select_value
                    Log To Console    ${value}
                    IF    ${value}
                        Select From List By Value    ${item['selector']}:${spec_var}     ${objdata["${spec_var}"]}
                    ELSE
                        Select From List By Label    ${item['selector']}:${spec_var}     ${objdata["${spec_var}"]}
                    END  
                     
                END
                Sleep    1s
                CONTINUE
            END
            ${str_submit}    Run Keyword And Return Status    Should Contain    ${type}    submit
            IF    ${str_submit}
                    Log To Console    ${item['name']}
                    Execute JavaScript    window.scrollTo(0, document.body.scrollHeight);
                    Wait Until Element Is Visible     ${item['selector']}:${item['name']}    timeout=1s
                    Wait Until Element Is Enabled    ${item['selector']}:${item['name']}    timeout=1s
                    #Click Button    ${item['selector']}:${item['name']} 
                    #Click Element    css=button.${item['name']}
                    Execute JavaScript    document.querySelector('.${item['name']}').click();
                    Log To Console    element clicked   
                    Sleep    1s
                    CONTINUE                                                    
            END
            ${str_button}    Run Keyword And Return Status    Should Contain    ${type}    button
            IF    ${str_button}
                    ${str_td}    Run Keyword And Return Status    Should Contain    ${item['tag']}    td
                    IF    ${str_td}
                       
                        ${spec}    Set Variable    ${item['name']}
                        ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                        Log To Console    ${spec}
                        Log To Console    ${contains_left_brace}
                        IF    ${contains_left_brace}
                            ${spec_var}    Replace String    ${spec}    {    ${EMPTY}
                            ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}
                            Click Button Based on Td Value    ${objdata['${spec_var}']}    ${type}
                        END  
                    ELSE
                        Execute JavaScript    window.scrollTo(0, document.body.scrollHeight);
                        #Wait Until Element Is Enabled    ${item['selector']}:${item['name']}    timeout=10s
                        Log To Console    button name is ${item['name']}
                        ${btn_id}    Run Keyword And Return Status    Should Contain    ${item['selector']}    id
                        IF    ${btn_id}
                            Execute JavaScript    var event = new MouseEvent('click', { bubbles: true, cancelable: true }); document.getElementById("${item['name']}").dispatchEvent(event);
                        END
                        ${btn_class}    Run Keyword And Return Status    Should Contain    ${item['selector']}    class
                        IF    ${btn_class}
                            IF    $item['tag'] == 'data_btn'
 
                                ${spec}    Set Variable    ${item['name']}
                                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
 
                                IF    ${contains_left_brace}
                                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY}    
                                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}
                               
                                    Click Button    xpath=//button[@data-bb-handler='${objdata['${spec_var}']}']
                                ELSE
                                    Click Button    xpath=//button[@data-bb-handler='${item['name']}']
                                END
                            ELSE     
                                
                                Execute JavaScript    document.querySelector('.${item['name']}').click();
                               
                            END                  
                        END
 
                        Sleep    1s
                        CONTINUE
                    END                
            END
            ${str_script}    Run Keyword And Return Status    Should Contain    ${type}    script
            IF    ${str_script}
                    Log To Console    ${item['name']}
                    #Execute JavaScript    window.scrollTo(0, document.body.scrollHeight);
                    #Wait Until Element Is Enabled    ${item['selector']}:${item['name']}    timeout=10s
                    Sleep    1s 
                    Log To Console    button name is ${item['name']}
                    Execute JavaScript    ${item['name']};
                    Sleep    1s

                    CONTINUE                 
            END
            ${str_form}    Run Keyword And Return Status    Should Contain    ${type}    form
            IF    ${str_form}
                    Log To Console    ${item['name']}
                    Submit Form    xpath=//form[@${item['selector']}='${item['name']}']
                    Sleep    1s
                    CONTINUE
            END
            
            ${str_radio}    Run Keyword And Return Status    Should Contain    ${type}    radio
            IF    ${str_radio}
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                    Log To Console    ${spec_var}
                    ${contains_td}    Run Keyword And Return Status    Should Contain    ${item['tag']}    td
                    IF    ${contains_td}
                       Select Radio Button Based On Td Value    ${objdata["${spec_var}"]}
                    ELSE
                        ${spec}    Set Variable    ${item['name']}
                        ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {

                        IF    ${contains_left_brace}
                            ${spec_var}    Replace String    ${spec}    {    ${EMPTY}    
                            ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}               
                           
                            # Find the associated radio input element using the same index
                            ${radio_button}    Get WebElement    xpath=//label[contains(text(), "${objdata['${spec_var}']}")]
                            
                            # Click the radio button
                            Click Element    ${radio_button}
                        ELSE
                           Select Radio Button    ${spec_var}        ${objdata["${spec_var}"]}
                        END
                    END
                    
                END
                Sleep    1s
                CONTINUE                       
            END
            ${str_page}    Run Keyword And Return Status    Should Contain    ${type}    url
            IF    ${str_page}
                     Log To Console    ${item['name']}
                     Wait Until Location Contains    ${item['name']}     #timeout=10s
                     ${current_url}    Get Location
                     Log To Console    ${current_url}
                     Should Contain    ${current_url}    ${item['name']} 
                     Sleep    1s
                     CONTINUE   
            END
            ${str_nava_tag}    Run Keyword And Return Status    Should Contain    ${type}    nav-link
            IF    ${str_nava_tag}  
                    Log To Console  Link name is ${item['name']}
                    Log To Console  A Tag name is ${item['name']}
                    Log To Console   ${str_nava_tag} 
                    ${spec}    Set Variable    ${item['name']}
                    ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                    Log To Console    ${spec}
                    Log To Console    ${contains_left_brace}
                    IF    ${contains_left_brace}
                        ${spec_var}    Replace String    ${spec}    {    ${EMPTY}
                        ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}                        
            
                        #Click Element    xpath=//a[contains(@${item['selector']}, '${spec_var}') and contains(text(), '${objdata['${spec_var}']}')]  # Click the correct link
                        ${str_a_span}  Run Keyword And Return Status    Should Contain    ${item['tag']}    a_span
                        IF    ${str_a_span}
                            Wait Until Element Is Visible    xpath=//a[.//span[text()='Dashboards']]    #timeout=10s
                            Click Element    xpath=//a[.//span[text()='Dashboards']]
                        ELSE
                            Wait Until Element Is Visible    xpath=//a[contains(.,'${objdata['${spec_var}']}')]    #timeout=10s
                            Click Element    xpath=//a[contains(.,'${objdata['${spec_var}']}')]
                        END
                        #Execute Javascript    return document.querySelector("${item['tag']}.${spec_var}:contains('${objdata['${spec_var}']}')").click();  
                        Sleep    1s
                        CONTINUE
                    END
            END
            
            ${str_link}    Run Keyword And Return Status    Should Contain    ${type}    link
            IF    ${str_link}
                ${str_a_tag}   Run Keyword And Return Status    Should Contain    ${item['tag']}    td_a_tag
                
                IF    ${str_a_tag}
                        Log To Console  A Tag name is ${item['name']}
                        Log To Console    ${str_a_tag}
                        ${spec}    Set Variable    ${item['name']}
                        ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                        Log To Console    ${spec}
                        Log To Console    ${contains_left_brace}
                        IF    ${contains_left_brace}
                            ${spec_var}    Replace String    ${spec}    {    ${EMPTY}
                            ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}
                            Click Button Based on Td Value   ${objdata['${spec_var}']}    ${type}
                        END
                ELSE
                     Log To Console  Link name is ${item['name']}
                     Wait Until Element Is Not Visible    xpath=//div[@class='blockUI blockOverlay']    #timeout=80s
                     Wait Until Element Is Visible    ${item['selector']}:${item['name']}    #timeout=10s
                     Wait Until Element Is Enabled    ${item['selector']}:${item['name']}    #timeout=10s
                     Click Link    ${item['selector']}=${item['name']}
                     Sleep     0.5s
                END
                Sleep    1s
                CONTINUE
            END
            ${str_h2}    Run Keyword And Return Status    Should Contain    ${type}    h2
            IF    ${str_h2}
                Log To Console    ${item['name']}
                ${spec}    Set Variable    ${item['name']}
                ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                Log To Console    ${spec}
                Log To Console    ${contains_left_brace} 
                IF    ${contains_left_brace}
                    ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                    ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}
                    Wait Until Element Is Not Visible    xpath=//h2[@${item['selector']}='${spec_var}' and text()='${objdata['${spec_var}']}']    #timeout=20s
                    
                ELSE
                Wait Until Element Is Not Visible    xpath=//h2[@${item['selector']}='${item['name']}']    #timeout=20s
                END
                Sleep    1s
                CONTINUE
            END
            ${str_loading}    Run Keyword And Return Status    Should Contain    ${type}    loading
            IF    ${str_loading}
                     Log To Console    ${item['name']}
                     Wait Until Element Is Not Visible    ${item['selector']}=${item['name']}    #timeout=20s
                     Sleep    1s
                     CONTINUE
            END
            ${str_modal}    Run Keyword And Return Status    Should Contain    ${type}    div
            IF    ${str_modal}
                    ${str_select}     Run Keyword And Return Status    Should Contain    ${item['tag']}    select
                    IF    ${str_select}
                        Log To Console    ${item['name']}
                        ${spec}    Set Variable    ${item['name']}
                        ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                        Log To Console    ${spec}
                        Log To Console    ${contains_left_brace} 
                        IF    ${contains_left_brace}
                            ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                            ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}
                            ${str_class}    Run Keyword And Return Status    Should Contain    ${item['selector']}    class
                            
                            IF    ${str_class}
                                ${contains_left_bracket}    Run Keyword And Return Status    Should Contain    ${spec_var}    [
                                IF    ${contains_left_bracket}
                                ${cleaned_string}    Replace String    ${spec_var}    [    ${EMPTY}
                                ${cleaned_string}    Replace String Using Regexp    ${cleaned_string}     \\d*    ${EMPTY}
                                ${cleaned_string}    Replace String    ${cleaned_string}    ]    ${EMPTY}
                                Log To Console    ${cleaned_string} 
                                
                                    Wait Until Element Is Visible    //div[contains(@${item['selector']},'${cleaned_string}') and text()='${objdata['${spec_var}']}']    timeout=2s
                                    Click Element    xpath=//div[contains(@${item['selector']},'${cleaned_string}') and text()='${objdata['${spec_var}']}']
                                ELSE
                                    Wait Until Element Is Visible    //div[contains(@${item['selector']},'${spec_var}') and text()='${objdata['${spec_var}']}']    timeout=2s
                                    Click Element    xpath=//div[contains(@${item['selector']},'${spec_var}') and text()='${objdata['${spec_var}']}']
                                END
                            END
                        ELSE
                            ${str_class}    Run Keyword And Return Status    Should Contain    ${item['selector']}    class
                            
                            IF    ${str_class}
                                Wait Until Element Is Visible    //div[contains(@${item['selector']},'${item['name']}')]    timeout=2s
                                Log To Console    element name class ${item['name']}
                                Click Element    xpath=//div[@${item['selector']}='${item['name']}']
                                Sleep    1s
                            ELSE
                                Wait Until Element Is Visible    //div[@${item['selector']}='${item['name']}']    timeout=2s
                                Log To Console    element name ${item['name']}
                                Click Element    xpath=//div[@${item['selector']}='${item['name']}']
                                Sleep    1s
                            END
                        END
                    ELSE 
                        Log To Console    ${item['name']}
                        ${spec}    Set Variable    ${item['name']}
                        ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                        Log To Console    ${spec}
                        Log To Console    ${contains_left_brace} 
                        IF    ${contains_left_brace}
                            ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                            ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY}
                            ${str_class}    Run Keyword And Return Status    Should Contain    ${item['selector']}    class
                            
                            IF    ${str_class}
                                Wait Until Element Is Visible    //div[contains(@${item['selector']},'${spec_Var}')]    timeout=2s
                            ELSE
                                Wait Until Element Is Visible    //div[@${item['selector']}='${spec_Var}']    timeout=2s
                            END
                        ELSE
                            ${str_class}    Run Keyword And Return Status    Should Contain    ${item['selector']}    class
                            
                            IF    ${str_class}
                                Wait Until Element Is Visible    //div[contains(@${item['selector']},'${item['name']}')]    timeout=2s
                            ELSE
                                Wait Until Element Is Visible    //div[@${item['selector']}='${item['name']}']    timeout=2s
                            END
                        END
                    END    
                    Sleep    1s
                    CONTINUE     
            END
            ${str_cb}    Run Keyword And Return Status    Should Contain    ${type}    checkbox
            IF    ${str_cb}
                    Log To Console    ${item['name']}
                    ${spec}    Set Variable    ${item['name']}
                    ${contains_left_brace}    Run Keyword And Return Status    Should Contain    ${spec}    {
                    Log To Console    ${spec}
                    Log To Console    ${contains_left_brace} 
                    IF    ${contains_left_brace}
                        ${spec_var}    Replace String    ${spec}    {    ${EMPTY} 
                        ${spec_var}    Replace String    ${spec_var}    }    ${EMPTY} 
                        ${checkbox}=  Get WebElement  xpath=//table[@${item['selector']}='${spec_Var}']//td[text()='${objdata['${spec_var}']}']/preceding-sibling::td/input[@type='checkbox']
                        Click Element   ${checkbox}
                    ELSE
                        Select Frame    xpath=//iframe[contains(@src, 'recaptcha')]
                        Wait Until Element Is Visible    xpath=//span[contains(@id,'recaptcha-anchor')]    #timeout=10s
                        ${checkbox}=  Get WebElement  xpath=//span[contains(@${item['selector']},'${item['name']}')]
                        Click Element   ${checkbox}
                        Sleep    10s
                        Unselect Frame 
                    END
                    Sleep    1s
                    CONTINUE
            END     
          
    END
    #Wait Until Element Is Visible    id:select_payment_site    20s
    Sleep    1s


Convert Template To Lists
    [Arguments]    ${yaml_content}
    @{lines}    Split To Lines    ${yaml_content}
    @{resls}    Create List
    
    FOR     ${line}    IN    @{lines}        
        @{ls}    Split String    ${line}
        &{my_dict}    Create Dictionary    tag=${ls}[0]    type=${ls}[1]    selector=${ls}[2]    name=${ls}[3]
        Append To List    ${resls}    ${my_dict}     
    END
    RETURN     @{resls}

Select Radio Button Based On Td Value
    [Arguments]    ${td_value}
    
    # Wait for the td with the specific value (e.g., PayPal) to appear
    Wait Until Element Is Visible    xpath=//tr/td[2][contains(text(),'${td_value}')]    #timeout=2s
    

    # Click the radio button based on the next td text
    Click Element    xpath=//tr[td[2][contains(text(),'${td_value}')]]/td[1]//input[@type='radio']

Click Button Based on Td Value
    [Arguments]    ${td_value}    ${type}

    IF    '${type}' == 'button'
        ${button}=    Get WebElement    xpath=//tr[td[contains(text(),'${td_value}')]]//input[contains(@class, 'btn')]
        Click Element    ${button}         # Click the button
    END

    IF    '${type}' == 'link'        
        Wait Until Element Is Visible    xpath=//tr[td[contains(text(),'${td_value}')]]//i[contains(@class, 'cancel_plan_btn')]    2s
        Click Element    xpath=//tr[td[contains(text(),'${td_value}')]]//i[contains(@class, 'cancel_plan_btn')]
    END

Close Application
    Close Browser

    

