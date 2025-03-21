#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Updates the Jira Project for Stories.
    Helps with Jira Align data cleanup where the wrong Jira Project was
    selected when the Story was originally created in Jira Align.
    Uses Jira Align POST calls with the Stories.
"""

from warnings import catch_warnings
import common
import cfg

# Maximum number of records to return for main data items
MAX = 10

####################################################################################################################################################################################
def main():
####################################################################################################################################################################################
# MAIN
  
    # Call a subfile that helps handle shared routines and variables between this file and other files like workitemparser, jathemes, etc
    cfg.init()
    
    # Collect api server and endpoint. Also collect all of the instance json infomation we need into arrays with CollectUsrMenuItems
    common.CollectApiInfo()
 
    # Collect all Program information and save it
    programArray = common.ReadAllItems('programs', MAX)
    print("A total of " + str(len(programArray)) + " Programs were retrieved from Jira Align")

    # Gather info from the user
    print("")
    storyID = int(input("Enter the Jira Align Story ID to fix: "))
    programID = int(input("Enter the Program ID for this Story: "))
    jiraProjectName = input("Enter the name of the Jira Project to use for this Story: ")
    
    # Hardcoded data for testing
    #storyID = 1234
    #programID = 123
    #jiraProjectName = "JIRAFOO"

    # Print out the name of the Program so it can be visually verified
    print("")
    print("Verify these are correct:")
    print(" Story ID to fix:           " + str(storyID))
    print(" Program ID of the Feature: " + str(programID))
    print(" Jira Project to use:       " + jiraProjectName)
    print("")

    aFeature = common.ReadOneItem('stories', storyID)

    print("  Attempting to fix the Jira Project...")
    header = {'Content-Type': 'application/json;odata.metadata=minimal;odata.streaming=true'}

    # Create the POST data    
    body = aFeature[0]
    # Clear some fields
    body.pop('id', None)
    body.pop('createDate', None)
    body.pop('self', None)
    body['jiraProjectKey'] = jiraProjectName
    # Create a copy of the Story
    response = common.PostToJiraAlign(header, body, True, True, 
                                        cfg.instanceurl + "/Stories")
    if (response.status_code == 201):
        print("  Story successfully copied in Jira Align to ID: " + str(response.text))

        # Now mark the old one as cancelled
    else:
        print("Story could not be copied")
        print(response.content)
        print(body)
        pass
                
    pass #eof

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################
