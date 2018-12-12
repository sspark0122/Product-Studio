from api_manager import GoogleApiManager as Gmanager

g_api_manager = Gmanager()
g_api_manager.init_connection()

while True:
	print("\n=============================================================================")
	print("Supported Platforms: [GoogleDrive], [Gmail], [All], [Image-Search], [Text-Detection]")
	user_query = input("What do you want to search for? Usage: [keyword], [platform]\n")
	user_input = user_query.split(', ')
	result = g_api_manager.search(user_input[1], user_input[0])
	
	print(result)