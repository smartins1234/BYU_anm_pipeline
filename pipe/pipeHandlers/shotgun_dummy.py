import shotgun_api3
import pprint

SERVER_PATH = ""
ASSET_SCRIPT_NAME = ''
ASSET_SCRIPT_KEY = ''

SHOT_SCRIPT_NAME = ''
SHOT_SCRIPT_KEY = ''

PROJECT_ID = -1

class ShotgunReader:
    def __init__(self):
        pass

    def getAssetLists(self):

        sg = shotgun_api3.Shotgun(SERVER_PATH, ASSET_SCRIPT_NAME, ASSET_SCRIPT_KEY)

        #pprint.pprint([symbol for symbol in sorted(dir(sg)) if not symbol.startswith('_')])

        fields = ['code', 'parents']
        filters = [
            ["project", "is", {"type": "Project", "id": PROJECT_ID}],
            ["sg_asset_type", "is_not", "Environment"]
        ]
        result = sg.find("Asset", filters=filters, fields=fields)
        '''result = sg.schema_field_read("Asset", project_entity={"type": "Project", "id": PROJECT_ID})
        result = pprint.pformat(result)
        result_file = open("result.txt", "w")
        result_file.write(str(result))
        result_file.close()'''

        #pprint.pprint(result)

        full_list = []
        name_list = []
        short_list = []
        short_name_list = []

        for asset in result:
            temp = {}
            temp["name"] = asset["code"].replace(" ", "")
            temp["children"] = []
            full_list.append(temp)
            name_list.append(asset["code"].replace(" ", ""))

        short_name_list = name_list[:]
            
        for asset in result:
            for par in asset["parents"]:
                if par["name"].replace(" ", "") in name_list:
                    parent = par["name"].replace(" ", "")
                    parent_asset = list(filter(lambda temp: temp["name"].replace(" ", "") == parent, short_list))
                    if len(parent_asset) == 0:
                        parent_asset = {}
                        parent_asset["name"] = parent
                        parent_asset["children"] = []
                        short_list.append(parent_asset)
                    else:
                        parent_asset = parent_asset[0]
                    parent_asset["children"].append(asset["code"].replace(" ", ""))
                    short_name_list.remove(asset["code"].replace(" ", ""))

        for name in short_name_list:
            asset = list(filter(lambda temp: temp["name"] == name, short_list))
            if len(asset) == 0:
                new = {}
                new["name"] = name
                new["children"] = [name]
                short_list.append(new)

        #pprint.pprint(short_list)
        #pprint.pprint(name_list)
        return [name_list, short_list]

    def getShotList(self):

        sg = shotgun_api3.Shotgun(SERVER_PATH, SHOT_SCRIPT_NAME, SHOT_SCRIPT_KEY)

        fields = ['code']
        filters = [
            ["project", "is", {"type": "Project", "id": PROJECT_ID}]
        ]

        result = sg.find("Shot", filters=filters, fields=fields)
        #pprint.pprint(result)
        #print(len(result))

        shot_list = []

        for shot in result:
            name = shot["code"]
            shot_list.append(name)

        return shot_list