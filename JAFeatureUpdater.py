#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Updates the PI and/or Description of all Features that match the specified criteria
    entered by the user.  Helps with Jira Align data cleanup for work completed in
    the past.  Uses Jira Align PATCH calls with the Features.
"""

from warnings import catch_warnings
import common
import cfg
import json

# Maximum number of records to return for main data items
MAX = 1000

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
    print(" PI to set Features to: " + common.get_key_info(releaseArray, newPIID))
    print("")

    # Collect selected information about all JA Features information and save it
    featureArray = common.ReadAllItems('features', MAX, programId)

    skippedFeatureCount = 0
    successfulChangeCount = 0
    failedChangeCount = 0
    batch = True
    matchFor2023Count = 0
    
    # Loop through all the features, looking for ones in the Unassigned Backlog,
    # that match the requested ProgramId and stateId.
    print("Searching through the features...")  
    for aFeature in featureArray:
        # If this feature is assigned to a PI, then skip it
        if 'releaseId' in aFeature:
            skippedFeatureCount = skippedFeatureCount + 1
            continue
        # Else this feature is NOT assigned to a PI (it's in the Unassigned Backlog)
        else:
            # If the Program matches what we are looking for
            if aFeature['programId'] == programId:
                # If the State of the feature matches what we are looking for
                if aFeature['state'] == stateId:
                    tmpStr = ""
                    print("")
                    tmpStr = tmpStr + "FEATURE: ID=" + str(aFeature['id']) +\
                        " State=" + str(aFeature['state'])
                    if 'externalKey' in aFeature:
                        tmpStr = tmpStr + " JIRA Key=" + aFeature['externalKey']
                    tmpStr = tmpStr +\
                          " Accepted Date=" + aFeature['acceptedDate'] +\
                          " Title=" + aFeature['title']
                    print(tmpStr)
                    
                    # Count of Features accepted in 2023
                    if ("2023-" in aFeature['acceptedDate']):
                        matchFor2023Count = matchFor2023Count + 1
                        
                    # Only prompt for features accepted in 2021 or 2022
                    if ("2021-" not in aFeature['acceptedDate']) and ("2022-" not in aFeature['acceptedDate']):
                        print("  Not accepted in 2021/2022, skipping")
                        skippedFeatureCount = skippedFeatureCount + 1
                        continue
                    
                    # If we are NOT in batch mode, then confirm before moving the feature
                    if (batch != True):
                        # Confirm that we want to move this feature
                        moveStory = input("DO YOU WANT TO MOVE THIS FEATURE? ")
                        if (moveStory != 'y'):
                            continue
                    else:
                        print("  Attempting to move the feature...")
                    
                        header = {'Content-Type': 'application/json;odata.metadata=minimal;odata.streaming=true'}

                        # If the Description is missing, use the Title in it's place for
                        # that PATCH so that it will work (since Description is a required
                        # field in Jira Align).
                        if ('description' not in aFeature):
                            # Create the PATCH data    
                            body = [{'value': 'foo', 'path': '/description','op': 'replace'}]
                            body[0]['value'] = aFeature['title']
                            # Update the Feature's Description in Jira Align with a PATCH
                            response = common.PatchToJiraAlign(header, body, True, True, 
                                                               cfg.instanceurl + "/Features/" + str(aFeature['id']))
                            if (response.status_code == 204):
                                # Create the PATCH data    
                                body = [{'value': 193, 'path': '/releaseId','op': 'replace'}] # 193 = placeholder number
                                body[0]['value'] = newPIID # update the placeholder
                            
                                # Update the Story in Jira Align with a PATCH
                                response = common.PatchToJiraAlign(header, body, True, True, 
                                                                   cfg.instanceurl + "/Features/" + str(aFeature['id']))
                                if (response.status_code == 204):
                                    print("  Feature successfully updated in Jira Align.")
                                    successfulChangeCount = successfulChangeCount + 1
                                else:
                                    print(response)
                                    failedChangeCount = failedChangeCount + 1
                                    foo = input("FAILURE")
                            else:
                                print("Description could not be updated, skipping this Feature")
                                failedChangeCount = failedChangeCount + 1
                else:
                    skippedFeatureCount = skippedFeatureCount + 1
            else:
                skippedFeatureCount = skippedFeatureCount + 1

    # Output operation summary
    print("")                    
    print(str(skippedFeatureCount) + " Features were skipped")
    print(str(successfulChangeCount) + " Features were successfully changed")
    print(str(failedChangeCount) + " Features failed to be changed")
    print(str(matchFor2023Count) + " Features Accepted in 2023")
                
    pass #eof

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################
