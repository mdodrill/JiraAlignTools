#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Updates the PI and/or Description of all Stories that match the specified criteria
    entered by the user.  Helps with Jira Align data cleanup for work completed in
    the past.  Uses Jira Align PATCH calls with the Stories.
"""

from warnings import catch_warnings
import common
import cfg
import json

# Maximum number of records to return for main data items
MAX = 10000

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

    # Collect all Release/PI information and save it
    releaseArray = common.ReadAllItems('releases', MAX)
    print("A total of " + str(len(releaseArray)) + " Releases/PIs were retrieved from Jira Align")

    # Gather info from the user
    print("")
    programId = int(input("Enter the Jira Align Program ID to search in: "))
    stateId = int(input("Enter the Jira Align State ID to search for (5 is Accepted): "))
    newPIID = int(input("Enter the NEW Jira Align PI ID (JA Release) to use: "))
    
    # Hardcoded data for testing
    #programId = 0
    #stateId = 5 # Accepted
    #newPIID = 0 #

    # Print out the name of the Program so it can be visually verified
    print("")
    print("Verify these are correct:")
    print(" Program to search in: " + common.get_key_info(programArray, programId))
    print(" PI to set Stories to: " + common.get_key_info(releaseArray, newPIID))
    print("")

    # Collect selected information about all JA Stories information and save it
    storyArray = common.ReadAllItems('stories', MAX, programId)

    skippedStoryCount = 0
    successfulChangeCount = 0
    failedChangeCount = 0
    batch = True
    matchFor2024Count = 0
    iteration = 1
    
    # Loop through all the stories, looking for ones in the Unassigned Backlog,
    # that match the requested ProgramId and stateId.
    print("Searching through the stories...")  
    for aStory in storyArray:
        # If this story is assigned to a PI, then skip it
        if 'releaseId' in aStory:
            skippedStoryCount = skippedStoryCount + 1
        # Else this story is NOT assigned to a PI (it's in the Unassigned Backlog)
        else:
            # If the Program matches what we are looking for
            if aStory['programId'] == programId:
                # If the State of the story matches what we are looking for
                if aStory['state'] == stateId:
                    tmpStr = ""
                    print("")
                    tmpStr = tmpStr + "(" + str(iteration) + ") STORY: ID=" + str(aStory['id']) +\
                        " State=" + str(aStory['state'])
                    if 'externalKey' in aStory:
                        tmpStr = tmpStr + " JIRA Key=" + aStory['externalKey']
                    tmpStr = tmpStr +\
                          " Accepted Date=" + aStory['acceptedDate'] +\
                          " Title=" + aStory['title']
                    print(tmpStr)
                    
                    # Count of Stories accepted in 2024
                    if ("2024-" in aStory['acceptedDate']):
                        matchFor2024Count = matchFor2024Count + 1
                        
                    # Only prompt for stories accepted in 2019 through 2023
                    if ("2019" not in aStory['acceptedDate']) and\
                         ("2020-" not in aStory['acceptedDate']) and\
                         ("2021-" not in aStory['acceptedDate']) and\
                         ("2022-" not in aStory['acceptedDate']) and\
                         ("2023-" not in aStory['acceptedDate']):
                        print("  Not accepted in 2019-2023, skipping")
                        skippedStoryCount = skippedStoryCount + 1
                        iteration = iteration + 1
                        continue
                    
                    # If we are NOT in batch mode, then confirm before moving the story
                    if (batch != True):
                        # Confirm that we want to move this story
                        moveStory = input("DO YOU WANT TO UPDATE THIS STORY? ")
                        if (moveStory != 'y'):
                            iteration = iteration + 1
                            continue
                    else:
                        print("  Attempting to update the story...")
                    
                        header = {'Content-Type': 'application/json;odata.metadata=minimal;odata.streaming=true'}

                        # Fix any invalid story point values
                        body = []
                        body.append({'value': 0, 'path': '/effortPoints','op': 'replace'}) # 0 is a dummy value

                        # If there is a Story Point value in the Story
                        if 'effortPoints' in aStory:
                            body[0]['value'] = aStory['effortPoints'] # Set to original value in the item
                        # No Story Point value in the story now, so set to zero
                        else:
                            aStory['effortPoints'] = 0
                            body[0]['value'] = 0

                        # Replace invalid Story Point values with valid ones
                        if aStory['effortPoints'] == 4:
                            body[0]['value'] = 3
                        elif aStory['effortPoints'] == 6:
                            body[0]['value'] = 5
                        elif aStory['effortPoints'] == 7:
                            body[0]['value'] = 8
                        elif aStory['effortPoints'] == 9:
                            body[0]['value'] = 8
                        elif aStory['effortPoints'] == 10:
                            body[0]['value'] = 8
                        elif aStory['effortPoints'] == 11:
                            body[0]['value'] = 13
                        elif aStory['effortPoints'] == 12:
                            body[0]['value'] = 13
                        elif aStory['effortPoints'] == 21:
                            body[0]['value'] = 20
                        else:
                            pass # Do nothing, the current value is fine

                        # If the Description is missing, use the Title in it's place for
                        # that PATCH so that it will work (since Description is a required
                        # field in Jira Align).
                        if ('description' not in aStory):
                            # Create the PATCH data    
                            body2 = {'value': 'foo', 'path': '/description','op': 'replace'}
                            body2['value'] = aStory['title']
                            body.append(body2)

                        # Create the PATCH data to update the PI
                        body3 = {'value': 193, 'path': '/releaseId','op': 'replace'} # 193 = placeholder number
                        body3['value'] = newPIID # update the placeholder
                        #print(body3)
                        body.append(body3)

                        # Update the Story in Jira Align with a PATCH
                        url = cfg.instanceurl + "/Stories/" + str(aStory['id'])
                        #print(url)
                        response = common.PatchToJiraAlign(header, body, True, True, url)
                        if (response.status_code == 204):
                            print("  Story successfully updated in Jira Align.")
                            successfulChangeCount = successfulChangeCount + 1
                        else:
                            print(response)
                            print(response.content)
                            print(url)
                            print(body)
                            failedChangeCount = failedChangeCount + 1
                            #foo = input("FAILURE")

                else:
                    skippedStoryCount = skippedStoryCount + 1
            else:
                skippedStoryCount = skippedStoryCount + 1
        iteration = iteration + 1

    # Output operation summary
    print("")                    
    print(str(skippedStoryCount) + " Stories were skipped")
    print(str(successfulChangeCount) + " Stories were successfully changed")
    print(str(failedChangeCount) + " Stories failed to be changed")
    print(str(matchFor2024Count) + " Stories Accepted in 2024")
                
    pass #eof

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################
