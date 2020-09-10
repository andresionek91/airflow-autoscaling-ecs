from jinja2 import Template

texto = """
{% if ENVIRONMENT == 'producao' %}

Resources:
  AirflowECSLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: "{{ serviceName }}-{{ ENVIRONMENT }}-ecs-log-group"
      RetentionInDays: "{{ cloudwatch.ecsLogGroup }}"
      
{% endif %}

Outputs:
  AirflowECSLogGroupName:
    Value: !Ref AirflowECSLogGroup
    Export:
      Name: cloudwatch-AirflowECSLogGroupName

"""

variaveis = dict(
    serviceName="airflow",
    ENVIRONMENT="dev",
    cloudwatch=dict(ecsLogGroup="bla")
)


texto_pronto = Template(texto).render(variaveis)
print(texto_pronto)