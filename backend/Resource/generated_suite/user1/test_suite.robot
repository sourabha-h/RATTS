*** Settings ***
Documentation    Gui Resources
Resource         D:\\RATTS_bluerise\\RATTS\\backend\\Resource\\gui_resources.robot
Suite Setup    login TC_BR_Login_001
Suite Teardown    Close Application

*** Keywords ***
login TC_BR_Login_001
    [Documentation]    login with Test Case  TC_BR_Login_001
    Open Application
    Page Action    {"username": "rajeswari@bluerose-tech.com", "password-input": "U238Vr%*7i3Lgab", "page-title-box": "Overview"}    login.yaml.template    login.html


*** Test Cases ***
Manager Test Case for login TC_BR_Login_001 TC_BR_DR_001
    [Documentation]    Manager with Test  TC_BR_DR_001
    Page Action    {"nav-item": "Team Stats", "page-title-box": "Manager Dashboard"}    manager.yaml.template    index.html

