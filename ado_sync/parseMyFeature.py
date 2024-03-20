import re
from gherkin3.parser import Parser
import yaml
import argparse

def convert_and_send(gherkin_filename):
    with open("/workspaces/rf_azure_sync/ado_sync/test.feature", 'r') as f:
        content = f.read()
    parser = Parser()
    feature = parser.parse(content)

    # print(yaml.dump(feature))
    for test in feature["scenarioDefinitions"]:
        convertedSteps = ""
        convertedExamples = ""
        convertedParams = ""
        if(len(test["steps"]) > 0):
            convertedSteps = convert_step_to_xml(test["steps"])
        if(test.get("examples") is not None):
            convertedExamples = convert_gherkin_examples_to_xml(test["examples"])
            convertedParams = convert_gherkin_parameters(test["examples"])

        print(convertedSteps)
        print(convertedExamples)
        print(convertedParams)

def convert_gherkin_parameters(gherkin_testcase):
    parameters = []

    for option in gherkin_testcase[0]["tableHeader"]["cells"]:
        param_element = f'<param name=\"{option["value"]}\" bind=\"default\"/>'
        parameters.append(param_element)

    paramToSend = f"<parameters>"
    paramToSend += '\n'.join(parameters)
    paramToSend += f"</parameters>"

    return paramToSend

def convert_gherkin_examples_to_xml(gherkin_examples):
    header_elements = []

    header_cell = []

    for option in gherkin_examples[0]["tableHeader"]["cells"]:
        header_element = f"<xs:element name='{option['value']}' type='xs:string' minOccurs='0' />"
        header_elements.append(header_element)
        header_cell.append(option['value'])

    header = f"""<xs:schema id='NewDataSet' xmlns:xs='http://www.w3.org/2001/XMLSchema' xmlns:msdata='urn:schemas-microsoft-com:xml-msdata'>
    <xs:element name='NewDataSet' msdata:IsDataSet='true' msdata:Locale=''>
        <xs:complexType>
            <xs:choice minOccurs='0' maxOccurs = 'unbounded'>
                <xs:element name='Table1'>
                    <xs:complexType>
                        <xs:sequence>"""
    header += '\n'.join(header_elements)
    header += f"""</xs:sequence>
                        </xs:complexType>
                    </xs:element>
                </xs:choice>
            </xs:complexType>
        </xs:element>
    </xs:schema>"""

    body_elements = []
    for body_item in gherkin_examples[0]["tableBody"]:
        body_element = ""
        for i, el in enumerate(body_item["cells"]):
            body_element += f"<{header_cell[i]}>{el['value']}</{header_cell[i]}>"
        body_element = f"<Table1>{body_element}</Table1>"
        body_elements.append(body_element)
    
    dataset = f"<NewDataSet>{header}{body_elements}</NewDataSet>"

    return dataset

def convert_step_to_xml(steps):
    pattern = r'<(.*?)>'
    xml_steps = []
    for idx, step in enumerate(steps, start=2):
        stepText = re.sub(pattern, r'@\1', step["text"])
        xml_step = f'<step id="{idx}" type="ActionStep">\n'
        xml_step += f'    <parameterizedString isformatted="true">&lt;DIV&gt;&lt;P&gt; {step["type"]} {step["keyword"]} {stepText}&lt;/P&gt;&lt;/DIV&gt;</parameterizedString>\n'
        xml_step += '    <parameterizedString isformatted="true">&lt;DIV&gt;&lt;P&gt;&lt;BR/&gt;&lt;/P&gt;&lt;/DIV&gt;</parameterizedString>\n'
        xml_step += '    <description/>\n'
        xml_step += '</step>'
        xml_steps.append(xml_step)

    xml = f'<steps id="0" last="{idx}">\n'
    xml += '\n'.join(xml_steps)
    xml += '\n</steps>'

    return xml

def main():
    # cmdlineparser = argparse.ArgumentParser()
    # cmdlineparser.add_argument("feature")
    # cmdline_args = cmdlineparser.parse_args()
    convert_and_send("test.feature")


if __name__ == '__main__':
    main()