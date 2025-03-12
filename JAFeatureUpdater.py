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
MAX = 20000

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
    featureArray = common.ReadAllItems('features', MAX)

    skippedFeatureCount = 0
    successfulChangeCount = 0
    failedChangeCount = 0
    batch = True
    matchFor2024Count = 0
    iteration = 1
    
    # Loop through all the features, looking for ones in the Unassigned Backlog,
    # that match the requested ProgramId and stateId.
    print("Searching through the features...")  
    for aFeature in featureArray:
        # If this feature is assigned to a PI, then skip it
        if 'releaseId' in aFeature:
            skippedFeatureCount = skippedFeatureCount + 1
        # Else this feature is NOT assigned to a PI (it's in the Unassigned Backlog)
        else:
            # If the Program matches what we are looking for
            if aFeature['primaryProgramId'] == programId:
                # If the State of the feature matches what we are looking for
                if aFeature['state'] == stateId:
                    tmpStr = ""
                    print("")
                    tmpStr = tmpStr + "(" + str(iteration) + ") Feature: ID=" + str(aFeature['id']) +\
                        " State=" + str(aFeature['state'])
                    if 'externalKey' in aFeature:
                        tmpStr = tmpStr + " JIRA Key=" + aFeature['externalKey']
                    tmpStr = tmpStr +\
                          " Accepted Date=" + aFeature['acceptedDate'] +\
                          " Title=" + aFeature['title']
                    print(tmpStr)
                    
                    # Count of Stories accepted in 2024
                    if ("2024-" in aFeature['acceptedDate']):
                        matchFor2024Count = matchFor2024Count + 1
                        
                    # Only prompt for stories accepted in 2019 through 2023
                    if ("2019" not in aFeature['acceptedDate']) and\
                         ("2020-" not in aFeature['acceptedDate']) and\
                         ("2021-" not in aFeature['acceptedDate']) and\
                         ("2022-" not in aFeature['acceptedDate']) and\
                         ("2023-" not in aFeature['acceptedDate']):
                        print("  Not accepted in 2019-2023, skipping")
                        skippedFeatureCount = skippedFeatureCount + 1
                        iteration = iteration + 1
                        continue
                    
                    # If we are NOT in batch mode, then confirm before moving the feature
                    if (batch != True):
                        # Confirm that we want to move this feature
                        moveFeature = input("DO YOU WANT TO UPDATE THIS FEATURE? ")
                        if (moveFeature != 'y'):
                            iteration = iteration + 1
                            continue
                    else:
                        print("  Attempting to update the feature...")
                    
                        header = {'Content-Type': 'application/json;odata.metadata=minimal;odata.streaming=true'}
                        body = []

                        # If the Description is missing, use the Title in it's place for
                        # that PATCH so that it will work (since Description is a required
                        # field in Jira Align).
                        if ('description' not in aFeature):
                            # Create the PATCH data    
                            body2 = {'value': 'foo', 'path': '/description','op': 'replace'}
                            body2['value'] = aFeature['title']
                            body.append(body2)

                        # Create the PATCH data to update the PI
                        body3 = {'value': 193, 'path': '/releaseId','op': 'replace'} # 193 = placeholder number
                        body3['value'] = newPIID # update the placeholder
                        #print(body3)
                        body.append(body3)

                        # Update the Feature in Jira Align with a PATCH
                        url = cfg.instanceurl + "/Features/" + str(aFeature['id'])
                        #print(url)
                        response = common.PatchToJiraAlign(header, body, True, True, url)
                        if (response.status_code == 204):
                            print("  Feature successfully updated in Jira Align.")
                            successfulChangeCount = successfulChangeCount + 1
                        else:
                            print(response)
                            print(response.content)
                            print(url)
                            print(body)
                            failedChangeCount = failedChangeCount + 1
                else:
                    skippedFeatureCount = skippedFeatureCount + 1
            else:
                skippedFeatureCount = skippedFeatureCount + 1
        iteration = iteration + 1

    # Output operation summary
    print("")                    
    print(str(skippedFeatureCount) + " Features were skipped")
    print(str(successfulChangeCount) + " Features were successfully changed")
    print(str(failedChangeCount) + " Features failed to be changed")
    print(str(matchFor2024Count) + " Features Accepted in 2024")
                
    pass #eof

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################
