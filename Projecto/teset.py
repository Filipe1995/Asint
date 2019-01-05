import json
with open('Users', 'r') as feedjson:
        feed=json.load(feedjson)
        print(feed)
            #if feed=="-":
            #    return json.dumps("-1")
            #list=[]
            #for ID in feed:
            #    list.append(ID)

#            if list:
#                    print(list)
#                    return json.dumps(list)
#            else:
#                    return json.dumps("-1")
