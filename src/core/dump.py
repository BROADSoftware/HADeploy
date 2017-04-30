
import os
import pprint
import yaml
from const import SRC,DATA,HELPER


def dumpModel(context):
    if SRC in context.model:
        path = os.path.normpath(os.path.join(context.workingFolder, "model_src.json"))
        output = file(path, 'w')
        pp = pprint.PrettyPrinter(indent=2, stream=output)
        pp.pprint(context.model[SRC])
        output.close()
    if DATA in context.model:
        path = os.path.normpath(os.path.join(context.workingFolder, "model_data.json"))
        output = file(path, 'w')
        pp = pprint.PrettyPrinter(indent=2, stream=output)
        pp.pprint(context.model[DATA])
        output.close()
    if HELPER in context.model:
        path = os.path.normpath(os.path.join(context.workingFolder, "model_helper.json"))
        output = file(path, 'w')
        pp = pprint.PrettyPrinter(indent=2, stream=output)
        pp.pprint(context.model[HELPER])
        output.close()


def dumpSchema(context, theSchema):
    path = os.path.normpath(os.path.join(context.workingFolder, "schema.yml"))
    output = file(path, 'w')
    yaml.dump(theSchema, output)
    output.close()