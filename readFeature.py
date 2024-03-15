import re

class Feature:
    def __init__(self, title, scenarios):
        self.title = title
        self.scenarios = scenarios

class Scenario:
    def __init__(self, title, tags, steps):
        self.title = title
        self.tags = tags
        self.steps = steps

def parse_feature_file(file_content):
    # Define regular expression patterns
    feature_pattern = re.compile(r'Funcionalidade: (.+?)\n((.*\n)+?)(?=\s*Cenário:|$)', re.DOTALL)
    scenario_pattern = re.compile(r'(@[\w:]+)?\s*Cenário: (.+?)((.*\n)+?)(?=\s*Cenário:|$)', re.DOTALL)
    step_pattern = re.compile(r'(Dado|Quando|Então) (.+?)\n')

    # Find features in the file content
    feature_matches = feature_pattern.finditer(file_content)

    features = []
    for feature_match in feature_matches:
        feature_title, scenarios_text = feature_match.groups()
        feature_title = feature_title.strip()

        # Find scenarios in the feature
        scenario_matches = scenario_pattern.finditer(scenarios_text)

        scenarios = []
        for scenario_match in scenario_matches:
            tags, scenario_title, steps_text = scenario_match.groups()
            tags = re.findall(r'@[\w:]+', tags or '')
            scenario_title = scenario_title.strip()

            # Find steps in the scenario
            step_matches = step_pattern.finditer(steps_text)
            steps = [(step_match.group(1), step_match.group(2).strip()) for step_match in step_matches]

            scenarios.append(Scenario(scenario_title, tags, steps))

        features.append(Feature(feature_title, scenarios))

    return features

def read_feature_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        feature_content = file.read()
    return feature_content

file_path = 'tests/test.feature'
feature_content = read_feature_file(file_path)
# Example usage
file_content = """
Funcionalidade: Anomalia de Agendamento Sem Checkin

@tc:68
@story:50
@ignore
Cenário: Derrubar no chão
    Dado que o gato pulou na estante
    Quando o gato encontrou um objeto
    Então p gato derruba o objeto no chão

@tc:69
@story:50
Cenário: Cenário 2
    Dado que o gato pulou na estante 1
    Quando o gato encontrou um  asfasd
    Então p gato derruba o objeto no chão 3
"""

features = parse_feature_file(feature_content)

# Display the results
for feature in features:
    print('Feature:', feature.title)
    for scenario in feature.scenarios:
        print('  Scenario:', scenario.title)
        print('    Tags:', scenario.tags)
        print('    Steps:')
        for step_type, step_text in scenario.steps:
            print(f'      {step_type}: {step_text}')
        print()
