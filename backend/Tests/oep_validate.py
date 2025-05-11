import xml.etree.ElementTree as ET


def get_status_code(xml_content):
    # Parse the corrected XML content
    root = ET.fromstring(xml_content)

    # Find the StatusCode element and get its value
    status_code = root.find('.//{http://dhiraagu.com.mv/OEP/OrderManagement/Order/V1}StatusCode').text

    return status_code

def get_status_description(xml_content):
    # Parse the corrected XML content
    root = ET.fromstring(xml_content)

    # Find the StatusCode element and get its value
    status_desc = root.find('.//{http://dhiraagu.com.mv/OEP/OrderManagement/Order/V1}StatusDescription').text

    return status_desc