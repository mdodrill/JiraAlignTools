#!/usr/bin/env python3
#
# common.py
#
# All common function used for various example programs.

import json
import time
import csv
from urllib.parse import urlparse

import cfg
import creds
import requests

# Set to True to see additional debug info on exact URLs used
DEBUG = False
# Set to True to use hardcoded values for API Endpoint and Instance URL
# Set to False to prompt each time
USE_DEFAULTS = True

def PatchToJiraAlign(header, paramData, verify_flag, use_bearer, url = None):
    """Generic method to do a PATCH to the Jira Align instance, with the specified parameters, and return
        the result of the PATCH call.

    Args:
        header: The HTTP header to use
        paramData: The data to PATCH
        verify_flag (bool): Either True or False
        use_bearer (bool): If True, use the BearerAuth token, else use username/token.
        url (string): The URL to use for the PATCH.  If None, use the default instance + API end point variables defined

    Returns:
        Response
    """
    if url is None:
        # Use the default URL
        url_to_use = cfg.instanceurl
    else:
        # Use the given URL
        url_to_use = url
    if DEBUG == True:
        print("Headers: " + header)
        print("Data: " + paramData)
        print("URL: " + url_to_use)
    # If we need to use BearerAuth with Token
    if use_bearer:
        result = requests.patch(url = url_to_use, data=json.dumps(paramData),
                               headers=header, 
                               verify=verify_flag, 
                               auth=cfg.BearerAuth(creds.jatoken))
    # Otherwise, use Username/Token auth
    else:
        result = requests.patch(url = url_to_use, data=json.dumps(paramData),
                               headers=header, verify=verify_flag, 
                               auth=(creds.username, creds.jatoken))
    return result

def PostToJiraAlign(header, paramData, verify_flag, use_bearer, url = None):
    """Generic method to do a POST to the Jira Align instance, with the specified parameters, and return
        the result of the POST call.

    Args:
        header: The HTTP header to use
        paramData: The data to POST
        verify_flag (bool): Either True or False
        use_bearer (bool): If True, use the BearerAuth token, else use username/token.
        url (string): The URL to use for the POST.  If None, use the default instance + API end point variables defined

    Returns:
        Response
    """
    if url is None:
        # Use the default URL
        url_to_use = cfg.instanceurl
    else:
        # Use the given URL
        url_to_use = url
    if DEBUG == True:
        print("URL: " + url_to_use)
    # If we need to use BearerAuth with Token
    if use_bearer:
        result = requests.post(url = url_to_use, data=json.dumps(paramData), 
                               headers=header, verify=verify_flag, 
                               auth=cfg.BearerAuth(creds.jatoken))
    # Otherwise, use Username/Token auth
    else:
        result = requests.post(url = url_to_use, data=json.dumps(paramData), 
                               headers=header, verify=verify_flag, 
                               auth=(creds.username, creds.jatoken))
    return result

def GetFromJiraAlign(use_bearer, url = None):
    """Generic method to do a GET to the Jira Align instance, with the specified parameters, and return
        the result of the GET call.

    Args:
        use_bearer (bool): If True, use the BearerAuth token, else use username/token.
        url (string): The URL to use for the GET.  If None, use the default instance + API end point variables defined

    Returns:
        Response
    """
    if url is None:
        # Use the default URL
        url_to_use = cfg.instanceurl
    else:
        # Use the given URL
        url_to_use = url
    if DEBUG == True:
        print("URL: " + url_to_use)

    # If we need to use BearerAuth with Token
    if use_bearer:
        result = requests.get(url = url_to_use, auth=cfg.BearerAuth(creds.jatoken))
    # Otherwise, use Username/Token auth
    else:
        result = requests.get(url = url_to_use, auth=(creds.usernamev1, creds.jatokenv1))
    return result

# This collects instance details like the url and the endpoint you want to target
def CollectApiInfo():
    print("Instance URL is normally something like:  https://foo.jiraalign.com")
    print("API Endpoint is normally: /")
    if USE_DEFAULTS == True:
        cfg.apiendpoint = "/"
        #cfg.instanceurl = "https://foo.jiraalign.com"
        cfg.instanceurl = "https://foo.jiraalign.com"
    else:
        cfg.apiendpoint = input("Enter the api endpoint for your instance in following format EG. ""cities"". It is very important that you spell this endpoint correctly. Please refer to the api documents E.G https://cprime.agilecraft.com/api-docs/public/ for the apiendpoints available : ")
        #print(apiendpoint)
        cfg.instanceurl = input("Enter the url for your instance in following format EG. ""https://cprime.agilecraft.com"" : ")
        ChkInput = input("Is this your correct instance and endpoint you want to work with?  " + cfg.instanceurl + " : " + cfg.apiendpoint + "  " + "\n")
        if (ChkInput == "N") or (ChkInput == "n"):
            CollectApiInfo()

    cfg.abouturl = cfg.instanceurl + "/About"
    cfg.instanceurl = cfg.instanceurl + "/rest/align/api/2" ##### Mess with these couple of lines, and break all of the other defs! 
    cfg.apiendpoint = "/" + cfg.apiendpoint.lower()
    cfg.api1instance = urlparse(cfg.instanceurl)
    cfg.api1instance = cfg.api1instance.scheme + "://" + cfg.api1instance.netloc
    cfg.api1instance = cfg.api1instance + "/api"
    print(cfg.instanceurl, cfg.api1instance)

    # Get the About page from Jira Align, and parse out the Jira Align version number from it
    aboutInfo = GetFromJiraAlign(False, cfg.abouturl)
    if DEBUG == True:
        print(aboutInfo.text)
    # This assumes a specific format/length of the JA version and won't work for SSO in most cases
    start = aboutInfo.text.find("data-version") + 14
    end = start + 14
    cfg.jaVersion = aboutInfo.text[start:end]
    
    return cfg.instanceurl, cfg.apiendpoint, cfg.api1instance

# APIv2 doesn't seem to support this.
def GetAllCountries():
    """ Get all Countries information and return to the caller.

        Returns: All the details for each country in a list of objects.
    """
    countryArr = []
    print("Collecting all Country info...")
    countries = GetFromJiraAlign(True, cfg.instanceurl + "/countries")
    dataCountry = countries.json()
    for eachCountry in dataCountry:
        itemDict = {}
        itemDict['id'] = eachCountry['id']
        itemDict['name'] = eachCountry['name']
        if eachCountry['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachCountry['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        countryArr.append(itemDict)
    return countryArr

def GetAllConnectorBoards():
    """ Get all Connector Board information and return to the caller.

        Returns: All the details for each connector board in a list of objects.
    """
    boardArr = []
    print("Collecting all Connector Board info...")
    boards = GetFromJiraAlign(True, cfg.instanceurl + "/connectors/1/boards")
    dataBoard = boards.json()
    for eachBoard in dataBoard:
        itemDict = {}
        itemDict['id'] = eachBoard['id']
        itemDict['areSprintsEnabled'] = eachBoard['areSprintsEnabled']
        itemDict['boardId'] = eachBoard['boardId']
        itemDict['boardName'] = eachBoard['boardName']
        itemDict['connectorId'] = eachBoard['connectorId']
        itemDict['createdBy'] = eachBoard['createdBy']
        itemDict['createDate'] = eachBoard['createDate']
        if eachBoard['errorMessage'] is not None:
            itemDict['errorMessage'] = eachBoard['errorMessage']
        itemDict['originSprints'] = eachBoard['originSprints']
        itemDict['programId'] = eachBoard['programId']
        itemDict['teamId'] = eachBoard['teamId']
        itemDict['teamName'] = eachBoard['teamName']
        if eachBoard['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachBoard['lastUpdatedBy']
        if eachBoard['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachBoard['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        boardArr.append(itemDict)
    return boardArr
    
def GetAllConnectorPriorities():
    """ Get all Connector Priority information and return to the caller.

        Returns: All the details for each connector priority in a list of objects.
    """
    prioritiesArr = []
    print("Collecting all Connector Priority info...")
    priorities = GetFromJiraAlign(True, cfg.instanceurl + "/connectors/1/priorities")
    dataPriority = priorities.json()
    for eachPriority in dataPriority:
        itemDict = {}
        itemDict['id'] = eachPriority['id']
        itemDict['connectorId'] = eachPriority['connectorId']
        if eachPriority['createdBy'] is not None:
            itemDict['createdBy'] = eachPriority['createdBy']
        if eachPriority['createDate'] is not None:
            itemDict['createDate'] = eachPriority['createDate']
        itemDict['itemTypeId'] = eachPriority['itemTypeId']
        itemDict['jiraPriorityId'] = eachPriority['jiraPriorityId']
        itemDict['jiraPriorityName'] = eachPriority['jiraPriorityName']
        itemDict['priorityId'] = eachPriority['priorityId']
        if eachPriority['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachPriority['lastUpdatedBy']
        if eachPriority['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachPriority['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        prioritiesArr.append(itemDict)
    return prioritiesArr
    
def GetAllConnectorProjects():
    """ Get all Connector Project information and return to the caller.

        Returns: All the details for each connector project in a list of objects.
    """
    projectsArr = []
    print("Collecting all Connector Project info...")
    projects = GetFromJiraAlign(True, cfg.instanceurl + "/connectors/1/projects")
    dataProject = projects.json()
    for eachProject in dataProject:
        itemDict = {}
        itemDict['id'] = eachProject['id']
        if eachProject['errorMessage'] is not None:
            itemDict['errorMessage'] = eachProject['errorMessage']
        itemDict['connectorId'] = eachProject['connectorId']
        itemDict['createdBy'] = eachProject['createdBy']
        itemDict['createDate'] = eachProject['createDate']
        itemDict['programId'] = eachProject['programId']
        itemDict['projectId'] = eachProject['projectId']
        itemDict['projectKey'] = eachProject['projectKey']
        itemDict['projectName'] = eachProject['projectName']
        if eachProject['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachProject['lastUpdatedBy']
        if eachProject['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachProject['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        projectsArr.append(itemDict)
    return projectsArr
    
def ExtractItemData(itemType, sourceItem, extractedData):
    """ Extract all applicable fields from the source item and add them to the extracted
        data, based on item type.
        Generic version, checks for a key's existance in the source before attempting to copy
        it over -- easier to maintain.

    Args:
        itemType: Which type of work the sourceItem is: epics, features, stories, defects, tasks, programs
        sourceItem: Full set of data for this item from Jira Align
        extractedData: All the data that needs to be saved from this sourceItem
    """
    # These will always exist
    extractedData['id'] = sourceItem['id']
    extractedData['itemtype'] = itemType
    
    # Check to see if each key exists in sourceItem, and if it does, then check to
    # see if the value is NOT None.  If it's not None, then copy the data over.
    if ('abilityToExec' in sourceItem) and (sourceItem['abilityToExec'] is not None):
        extractedData['abilityToExec'] = sourceItem['abilityToExec']
    if ('acceptedDate' in sourceItem) and (sourceItem['acceptedDate'] is not None):
        extractedData['acceptedDate'] = sourceItem['acceptedDate']
    if ('acceptedUserId' in sourceItem) and (sourceItem['acceptedUserId'] is not None):
        extractedData['acceptedUserId'] = sourceItem['acceptedUserId']
    if ('actualEndDate' in sourceItem) and (sourceItem['actualEndDate'] is not None):
        extractedData['actualEndDate'] = sourceItem['actualEndDate']
    if ('additionalProgramIds' in sourceItem) and (sourceItem['additionalProgramIds'] is not None):
        extractedData['additionalProgramIds'] = sourceItem['additionalProgramIds']
    if ('additionalProcessStepIds' in sourceItem) and (sourceItem['additionalProcessStepIds'] is not None):
        extractedData['additionalProcessStepIds'] = sourceItem['additionalProcessStepIds']
    if ('affectedCountryIds' in sourceItem) and (sourceItem['affectedCountryIds'] is not None):
        extractedData['affectedCountryIds'] = sourceItem['affectedCountryIds']
    if ('allowTaskDeletion' in sourceItem) and (sourceItem['allowTaskDeletion'] is not None):
        extractedData['allowTaskDeletion'] = sourceItem['allowTaskDeletion']
    if ('allowTeamToRunStandup' in sourceItem) and (sourceItem['allowTeamToRunStandup'] is not None):
        extractedData['allowTeamToRunStandup'] = sourceItem['allowTeamToRunStandup']
    if ('anchorSprint' in sourceItem) and (sourceItem['anchorSprint'] is not None):
        extractedData['anchorSprint'] = sourceItem['anchorSprint']
    if ('anchorSprintId' in sourceItem) and (sourceItem['anchorSprintId'] is not None):
        extractedData['anchorSprintId'] = sourceItem['anchorSprintId']
    if ('anchorSprintIds' in sourceItem) and (sourceItem['anchorSprintIds'] is not None):
        extractedData['anchorSprintIds'] = sourceItem['anchorSprintIds']
    if ('associatedTicket' in sourceItem) and (sourceItem['associatedTicket'] is not None):
        extractedData['associatedTicket'] = sourceItem['associatedTicket']
    if ('autoEstimateValue' in sourceItem) and (sourceItem['autoEstimateValue'] is not None):
        extractedData['autoEstimateValue'] = sourceItem['autoEstimateValue']
    if ('beginDate' in sourceItem) and (sourceItem['beginDate'] is not None):
        extractedData['beginDate'] = sourceItem['beginDate']
    if ('benefits' in sourceItem) and (sourceItem['benefits'] is not None):
        extractedData['benefits'] = sourceItem['benefits']
    if ('blendedHourlyRate' in sourceItem) and (sourceItem['blendedHourlyRate'] is not None):
        extractedData['blendedHourlyRate'] = sourceItem['blendedHourlyRate']
    if ('blockedReason' in sourceItem) and (sourceItem['blockedReason'] is not None):
        extractedData['blockedReason'] = sourceItem['blockedReason']
    if ('budget' in sourceItem) and (sourceItem['budget'] is not None):
        extractedData['budget'] = sourceItem['budget']
    if ('businessDriver' in sourceItem) and (sourceItem['businessDriver'] is not None):
        extractedData['businessDriver'] = sourceItem['businessDriver']
    if ('businessImpact' in sourceItem) and (sourceItem['businessImpact'] is not None):
        extractedData['businessImpact'] = sourceItem['businessImpact']
    if ('businessValue' in sourceItem) and (sourceItem['businessValue'] is not None):
        extractedData['businessValue'] = sourceItem['businessValue']
    if ('capitalized' in sourceItem) and (sourceItem['capitalized'] is not None):
        extractedData['capitalized'] = sourceItem['capitalized']
    if ('caseDevelopmentId' in sourceItem) and (sourceItem['caseDevelopmentId'] is not None):
        extractedData['caseDevelopmentId'] = sourceItem['caseDevelopmentId']
    if ('category' in sourceItem) and (sourceItem['category'] is not None):
        extractedData['category'] = sourceItem['category']
    if ('city' in sourceItem) and (sourceItem['city'] is not None):
        extractedData['city'] = sourceItem['city']
    if ('cityId' in sourceItem) and (sourceItem['cityId'] is not None):
        extractedData['cityId'] = sourceItem['cityId']
    if ('closeDate' in sourceItem) and (sourceItem['closeDate'] is not None):
        extractedData['closeDate'] = sourceItem['closeDate']
    if ('code' in sourceItem) and (sourceItem['code'] is not None):
        extractedData['code'] = sourceItem['code']
    if ('color' in sourceItem) and (sourceItem['color'] is not None):
        extractedData['color'] = sourceItem['color']
    if ('communityIds' in sourceItem) and (sourceItem['communityIds'] is not None):
        extractedData['communityIds'] = sourceItem['communityIds']
    if ('company' in sourceItem) and (sourceItem['company'] is not None):
        extractedData['company'] = sourceItem['company']
    if ('companyCode' in sourceItem) and (sourceItem['companyCode'] is not None):
        extractedData['companyCode'] = sourceItem['companyCode']
    if ('companyId' in sourceItem) and (sourceItem['companyId'] is not None):
        extractedData['companyId'] = sourceItem['companyId']
    if ('completedDate' in sourceItem) and (sourceItem['completedDate'] is not None):
        extractedData['completedDate'] = sourceItem['completedDate']
    if ('competitive' in sourceItem) and (sourceItem['competitive'] is not None):
        extractedData['competitive'] = sourceItem['competitive']
    if ('complexity' in sourceItem) and (sourceItem['complexity'] is not None):
        extractedData['complexity'] = sourceItem['complexity']
    if ('connectorExternalTeamMapping' in sourceItem) and (sourceItem['connectorExternalTeamMapping'] is not None):
        extractedData['connectorExternalTeamMapping'] = sourceItem['connectorExternalTeamMapping']
    if ('connectorId' in sourceItem) and (sourceItem['connectorId'] is not None):
        extractedData['connectorId'] = sourceItem['connectorId']
    if ('connectorJiraBoards' in sourceItem) and (sourceItem['connectorJiraBoards'] is not None):
        extractedData['connectorJiraBoards'] = sourceItem['connectorJiraBoards']
    if ('connectorJiraProjects' in sourceItem) and (sourceItem['connectorJiraProjects'] is not None):
        extractedData['connectorJiraProjects'] = sourceItem['connectorJiraProjects']
    if ('connectorPriorities' in sourceItem) and (sourceItem['connectorPriorities'] is not None):
        extractedData['connectorPriorities'] = sourceItem['connectorPriorities']
    if ('costCenter' in sourceItem) and (sourceItem['costCenter'] is not None):
        extractedData['costCenter'] = sourceItem['costCenter']
    if ('costCenterId' in sourceItem) and (sourceItem['costCenterId'] is not None):
        extractedData['costCenterId'] = sourceItem['costCenterId']
    if ('costCenterName' in sourceItem) and (sourceItem['costCenterName'] is not None):
        extractedData['costCenterName'] = sourceItem['costCenterName']
    if ('costCenters' in sourceItem) and (sourceItem['costCenters'] is not None):
        extractedData['costCenters'] = sourceItem['costCenters']
    if ('createDate' in sourceItem) and (sourceItem['createDate'] is not None):
        extractedData['createDate'] = sourceItem['createDate']
    if ('createdBy' in sourceItem) and (sourceItem['createdBy'] is not None):
        extractedData['createdBy'] = sourceItem['createdBy']
    if ('customerIds' in sourceItem) and (sourceItem['customerIds'] is not None):
        extractedData['customerIds'] = sourceItem['customerIds']
    if ('customers' in sourceItem) and (sourceItem['customers'] is not None):
        extractedData['customers'] = sourceItem['customers']
    if ('customFields' in sourceItem) and (sourceItem['customFields'] is not None):
        extractedData['customFields'] = sourceItem['customFields']
    if ('customhierarchies' in sourceItem) and (sourceItem['customhierarchies'] is not None):
        extractedData['customhierarchies'] = sourceItem['customhierarchies']
    if ('defectAllocation' in sourceItem) and (sourceItem['defectAllocation'] is not None):
        extractedData['defectAllocation'] = sourceItem['defectAllocation']
    if ('deliveredValue' in sourceItem) and (sourceItem['deliveredValue'] is not None):
        extractedData['deliveredValue'] = sourceItem['deliveredValue']
    if ('dependencyIds' in sourceItem) and (sourceItem['dependencyIds'] is not None):
        extractedData['dependencyIds'] = sourceItem['dependencyIds']
    if ('description' in sourceItem) and (sourceItem['description'] is not None):
        extractedData['description'] = sourceItem['description']
    if ('descriptionRich' in sourceItem) and (sourceItem['descriptionRich'] is not None):
        extractedData['descriptionRich'] = sourceItem['descriptionRich']
    if ('dependency' in sourceItem) and (sourceItem['dependency'] is not None):
        extractedData['dependency'] = sourceItem['dependency']
    if ('dependencyIds' in sourceItem) and (sourceItem['dependencyIds'] is not None):
        extractedData['dependencyIds'] = sourceItem['dependencyIds']
    if ('designStage' in sourceItem) and (sourceItem['designStage'] is not None):
        extractedData['designStage'] = sourceItem['designStage']
    if ('devCompleteBy' in sourceItem) and (sourceItem['devCompleteBy'] is not None):
        extractedData['devCompleteBy'] = sourceItem['devCompleteBy']
    if ('devCompleteDate' in sourceItem) and (sourceItem['devCompleteDate'] is not None):
        extractedData['devCompleteDate'] = sourceItem['devCompleteDate']
    if ('discountRate' in sourceItem) and (sourceItem['discountRate'] is not None):
        extractedData['discountRate'] = sourceItem['discountRate']
    if ('division' in sourceItem) and (sourceItem['division'] is not None):
        extractedData['division'] = sourceItem['division']
    if ('divisionCategory' in sourceItem) and (sourceItem['divisionCategory'] is not None):
        extractedData['divisionCategory'] = sourceItem['divisionCategory']
    if ('divisionCategoryName' in sourceItem) and (sourceItem['divisionCategoryName'] is not None):
        extractedData['divisionCategoryName'] = sourceItem['divisionCategoryName']
    if ('divisionId' in sourceItem) and (sourceItem['divisionId'] is not None):
        extractedData['divisionId'] = sourceItem['divisionId']
    if ('domains' in sourceItem) and (sourceItem['domains'] is not None):
        extractedData['domains'] = sourceItem['domains']
    if ('efficiencyDividend' in sourceItem) and (sourceItem['efficiencyDividend'] is not None):
        extractedData['efficiencyDividend'] = sourceItem['efficiencyDividend']
    if ('effortHours' in sourceItem) and (sourceItem['effortHours'] is not None):
        extractedData['effortHours'] = sourceItem['effortHours']
    if ('effortPoints' in sourceItem) and (sourceItem['effortPoints'] is not None):
        extractedData['effortPoints'] = sourceItem['effortPoints']
    if ('effortSwag' in sourceItem) and (sourceItem['effortSwag'] is not None):
        extractedData['effortSwag'] = sourceItem['effortSwag']
    if ('email' in sourceItem) and (sourceItem['email'] is not None):
        extractedData['email'] = sourceItem['email']
    if ('employeeClassification' in sourceItem) and (sourceItem['employeeClassification'] is not None):
        extractedData['employeeClassification'] = sourceItem['employeeClassification']
    if ('employeeId' in sourceItem) and (sourceItem['employeeId'] is not None):
        extractedData['employeeId'] = sourceItem['employeeId']
    if ('enableAutoEstimate' in sourceItem) and (sourceItem['enableAutoEstimate'] is not None):
        extractedData['enableAutoEstimate'] = sourceItem['enableAutoEstimate']
    if ('endDate' in sourceItem) and (sourceItem['endDate'] is not None):
        extractedData['endDate'] = sourceItem['endDate']
    if ('endSprintId' in sourceItem) and (sourceItem['endSprintId'] is not None):
        extractedData['endSprintId'] = sourceItem['endSprintId']
    if ('enterpriseHierarchy' in sourceItem) and (sourceItem['enterpriseHierarchy'] is not None):
        extractedData['enterpriseHierarchy'] = sourceItem['enterpriseHierarchy']
    if ('enterpriseHierarchyId' in sourceItem) and (sourceItem['enterpriseHierarchyId'] is not None):
        extractedData['enterpriseHierarchyId'] = sourceItem['enterpriseHierarchyId']
    if ('epicObjectId' in sourceItem) and (sourceItem['epicObjectId'] is not None):
        extractedData['epicObjectId'] = sourceItem['epicObjectId']
    if ('estimateAtCompletion' in sourceItem) and (sourceItem['estimateAtCompletion'] is not None):
        extractedData['estimateAtCompletion'] = sourceItem['estimateAtCompletion']
    if ('estimateTshirt' in sourceItem) and (sourceItem['estimateTshirt'] is not None):
        extractedData['estimateTshirt'] = sourceItem['estimateTshirt']
    if ('estimationEffortPercent' in sourceItem) and (sourceItem['estimationEffortPercent'] is not None):
        extractedData['estimationEffortPercent'] = sourceItem['estimationEffortPercent']
    if ('expenseSavings' in sourceItem) and (sourceItem['expenseSavings'] is not None):
        extractedData['expenseSavings'] = sourceItem['expenseSavings']
    if ('externalCapEx' in sourceItem) and (sourceItem['externalCapEx'] is not None):
        extractedData['externalCapEx'] = sourceItem['externalCapEx']
    if ('externalId' in sourceItem) and (sourceItem['externalId'] is not None):
        extractedData['externalId'] = sourceItem['externalId']
    if ('externalKey' in sourceItem) and (sourceItem['externalKey'] is not None):
        extractedData['externalKey'] = sourceItem['externalKey']
    if ('externalOpEx' in sourceItem) and (sourceItem['externalOpEx'] is not None):
        extractedData['externalOpEx'] = sourceItem['externalOpEx']
    if ('externalProject' in sourceItem) and (sourceItem['externalProject'] is not None):
        extractedData['externalProject'] = sourceItem['externalProject']
    if ('externalUser' in sourceItem) and (sourceItem['externalUser'] is not None):
        extractedData['externalUser'] = sourceItem['externalUser']
    if ('failureImpact' in sourceItem) and (sourceItem['failureImpact'] is not None):
        extractedData['failureImpact'] = sourceItem['failureImpact']
    if ('failureProbability' in sourceItem) and (sourceItem['failureProbability'] is not None):
        extractedData['failureProbability'] = sourceItem['failureProbability']
    if ('feasibility' in sourceItem) and (sourceItem['feasibility'] is not None):
        extractedData['feasibility'] = sourceItem['feasibility']
    if ('featureId' in sourceItem) and (sourceItem['featureId'] is not None):
        extractedData['featureId'] = sourceItem['featureId']
    if ('featureIds' in sourceItem) and (sourceItem['featureIds'] is not None):
        extractedData['featureIds'] = sourceItem['featureIds']
    if ('featureRank' in sourceItem) and (sourceItem['featureRank'] is not None):
        extractedData['featureRank'] = sourceItem['featureRank']
    if ('featureSummary' in sourceItem) and (sourceItem['featureSummary'] is not None):
        extractedData['featureSummary'] = sourceItem['featureSummary']
    if ('fcastShare' in sourceItem) and (sourceItem['fcastShare'] is not None):
        extractedData['fcastShare'] = sourceItem['fcastShare']
    if ('firstName' in sourceItem) and (sourceItem['firstName'] is not None):
        extractedData['firstName'] = sourceItem['firstName']
    if ('flag' in sourceItem) and (sourceItem['flag'] is not None):
        extractedData['flag'] = sourceItem['flag']
    if ('forecastYears' in sourceItem) and (sourceItem['forecastYears'] is not None):
        extractedData['forecastYears'] = sourceItem['forecastYears']
    if ('functionalArea' in sourceItem) and (sourceItem['functionalArea'] is not None):
        extractedData['functionalArea'] = sourceItem['functionalArea']
    if ('fullName' in sourceItem) and (sourceItem['fullName'] is not None):
        extractedData['fullName'] = sourceItem['fullName']
    if ('fundingStage' in sourceItem) and (sourceItem['fundingStage'] is not None):
        extractedData['fundingStage'] = sourceItem['fundingStage']
    if ('goal' in sourceItem) and (sourceItem['goal'] is not None):
        extractedData['goal'] = sourceItem['goal']
    if ('goalId' in sourceItem) and (sourceItem['goalId'] is not None):
        extractedData['goalId'] = sourceItem['goalId']
    if ('goalParent' in sourceItem) and (sourceItem['goalParent'] is not None):
        extractedData['goalParent'] = sourceItem['goalParent']
    if ('goalQuarter' in sourceItem) and (sourceItem['goalQuarter'] is not None):
        extractedData['goalQuarter'] = sourceItem['goalQuarter']
    if ('goals' in sourceItem) and (sourceItem['goals'] is not None):
        extractedData['goals'] = sourceItem['goals']
    if ('goalState' in sourceItem) and (sourceItem['goalState'] is not None):
        extractedData['goalState'] = sourceItem['goalState']
    if ('goalType' in sourceItem) and (sourceItem['goalType'] is not None):
        extractedData['goalType'] = sourceItem['goalType']
    if ('goalYear' in sourceItem) and (sourceItem['goalYear'] is not None):
        extractedData['goalYear'] = sourceItem['goalYear']
    if ('GridConfigurationsCapabilities' in sourceItem) and (sourceItem['GridConfigurationsCapabilities'] is not None):
        extractedData['GridConfigurationsCapabilities'] = sourceItem['GridConfigurationsCapabilities']
    if ('GridConfigurationsDependencies' in sourceItem) and (sourceItem['GridConfigurationsDependencies'] is not None):
        extractedData['GridConfigurationsDependencies'] = sourceItem['GridConfigurationsDependencies']
    if ('GridConfigurationsEpics' in sourceItem) and (sourceItem['GridConfigurationsEpics'] is not None):
        extractedData['GridConfigurationsEpics'] = sourceItem['GridConfigurationsEpics']
    if ('GridConfigurationsFeatures' in sourceItem) and (sourceItem['GridConfigurationsFeatures'] is not None):
        extractedData['GridConfigurationsFeatures'] = sourceItem['GridConfigurationsFeatures']
    if ('GridConfigurationsThemes' in sourceItem) and (sourceItem['GridConfigurationsThemes'] is not None):
        extractedData['GridConfigurationsThemes'] = sourceItem['GridConfigurationsThemes']
    if ('health' in sourceItem) and (sourceItem['health'] is not None):
        extractedData['health'] = sourceItem['health']
    if ('holidayCalendar' in sourceItem) and (sourceItem['holidayCalendar'] is not None):
        extractedData['holidayCalendar'] = sourceItem['holidayCalendar']
    if ('holidayCity' in sourceItem) and (sourceItem['holidayCity'] is not None):
        extractedData['holidayCity'] = sourceItem['holidayCity']
    if ('holidayCityId' in sourceItem) and (sourceItem['holidayCityId'] is not None):
        extractedData['holidayCityId'] = sourceItem['holidayCityId']
    if ('holidayRegionId' in sourceItem) and (sourceItem['holidayRegionId'] is not None):
        extractedData['holidayRegionId'] = sourceItem['holidayRegionId']
    if ('hourlyRate' in sourceItem) and (sourceItem['hourlyRate'] is not None):
        extractedData['hourlyRate'] = sourceItem['hourlyRate']
    if ('hoursEstimate' in sourceItem) and (sourceItem['hoursEstimate'] is not None):
        extractedData['hoursEstimate'] = sourceItem['hoursEstimate']
    if ('hypothesis' in sourceItem) and (sourceItem['hypothesis'] is not None):
        extractedData['hypothesis'] = sourceItem['hypothesis']
    if ('impedimentIds' in sourceItem) and (sourceItem['impedimentIds'] is not None):
        extractedData['impedimentIds'] = sourceItem['impedimentIds']
    if ('ideas' in sourceItem) and (sourceItem['ideas'] is not None):
        extractedData['ideas'] = sourceItem['ideas']
    if ('identifier' in sourceItem) and (sourceItem['identifier'] is not None):
        extractedData['identifier'] = sourceItem['identifier']
    if ('image' in sourceItem) and (sourceItem['image'] is not None):
        extractedData['image'] = sourceItem['image']
    if ('impedimentIds' in sourceItem) and (sourceItem['impedimentIds'] is not None):
        extractedData['impedimentIds'] = sourceItem['impedimentIds']
    if ('importance' in sourceItem) and (sourceItem['importance'] is not None):
        extractedData['importance'] = sourceItem['importance']
    if ('includeHours' in sourceItem) and (sourceItem['includeHours'] is not None):
        extractedData['includeHours'] = sourceItem['includeHours']
    if ('initialInvestment' in sourceItem) and (sourceItem['initialInvestment'] is not None):
        extractedData['initialInvestment'] = sourceItem['initialInvestment']
    if ('inProgressBy' in sourceItem) and (sourceItem['inProgressBy'] is not None):
        extractedData['inProgressBy'] = sourceItem['inProgressBy']
    if ('inProgressDate' in sourceItem) and (sourceItem['inProgressDate'] is not None):
        extractedData['inProgressDate'] = sourceItem['inProgressDate']
    if ('inProgressDateEnd' in sourceItem) and (sourceItem['inProgressDateEnd'] is not None):
        extractedData['inProgressDateEnd'] = sourceItem['inProgressDateEnd']
    if ('inScope' in sourceItem) and (sourceItem['inScope'] is not None):
        extractedData['inScope'] = sourceItem['inScope']
    if ('intakeFormId' in sourceItem) and (sourceItem['intakeFormId'] is not None):
        extractedData['intakeFormId'] = sourceItem['intakeFormId']
    if ('investmentType' in sourceItem) and (sourceItem['investmentType'] is not None):
        extractedData['investmentType'] = sourceItem['investmentType']
    if ('isActive' in sourceItem) and (sourceItem['isActive'] is not None):
        extractedData['isActive'] = sourceItem['isActive']
    if ('isBlocked' in sourceItem) and (sourceItem['isBlocked'] is not None):
        extractedData['isBlocked'] = sourceItem['isBlocked']
    if ('isCanceled' in sourceItem) and (sourceItem['isCanceled'] is not None):
        extractedData['isCanceled'] = sourceItem['isCanceled']
    if ('isComplianceManager' in sourceItem) and (sourceItem['isComplianceManager'] is not None):
        extractedData['isComplianceManager'] = sourceItem['isComplianceManager']
    if ('isExternal' in sourceItem) and (sourceItem['isExternal'] is not None):
        extractedData['isExternal'] = sourceItem['isExternal']
    if ('isImport' in sourceItem) and (sourceItem['isImport'] is not None):
        extractedData['isImport'] = sourceItem['isImport']
    if ('isKanbanTeam' in sourceItem) and (sourceItem['isKanbanTeam'] is not None):
        extractedData['isKanbanTeam'] = sourceItem['isKanbanTeam']
    if ('isLocked' in sourceItem) and (sourceItem['isLocked'] is not None):
        extractedData['isLocked'] = sourceItem['isLocked']
    if ('isMultiProgram' in sourceItem) and (sourceItem['isMultiProgram'] is not None):
        extractedData['isMultiProgram'] = sourceItem['isMultiProgram']
    if ('isRecycled' in sourceItem) and (sourceItem['isRecycled'] is not None):
        extractedData['isRecycled'] = sourceItem['isRecycled']
    if ('isSolution' in sourceItem) and (sourceItem['isSolution'] is not None):
        extractedData['isSolution'] = sourceItem['isSolution']
    if ('isSplit' in sourceItem) and (sourceItem['isSplit'] is not None):
        extractedData['isSplit'] = sourceItem['isSplit']
    if ('isSystemRole' in sourceItem) and (sourceItem['isSystemRole'] is not None):
        extractedData['isSystemRole'] = sourceItem['isSystemRole']
    if ('isTimeTracking' in sourceItem) and (sourceItem['isTimeTracking'] is not None):
        extractedData['isTimeTracking'] = sourceItem['isTimeTracking']
    if ('isUserManager' in sourceItem) and (sourceItem['isUserManager'] is not None):
        extractedData['isUserManager'] = sourceItem['isUserManager']
    if ('itemToSyncDate' in sourceItem) and (sourceItem['itemToSyncDate'] is not None):
        extractedData['itemToSyncDate'] = sourceItem['itemToSyncDate']
    if ('iterationId' in sourceItem) and (sourceItem['iterationId'] is not None):
        extractedData['iterationId'] = sourceItem['iterationId']
    if ('iterationSort' in sourceItem) and (sourceItem['iterationSort'] is not None):
        extractedData['iterationSort'] = sourceItem['iterationSort']
    if ('itemtype' in sourceItem) and (sourceItem['itemtype'] is not None):
        extractedData['itemtype'] = sourceItem['itemtype']
    if ('itemTypeId' in sourceItem) and (sourceItem['itemTypeId'] is not None):
        extractedData['itemTypeId'] = sourceItem['itemTypeId']
    if ('iterations' in sourceItem) and (sourceItem['iterations'] is not None):
        extractedData['iterations'] = sourceItem['iterations']
    if ('itrisk' in sourceItem) and (sourceItem['itrisk'] is not None):
        extractedData['itrisk'] = sourceItem['itrisk']
    if ('itRisk' in sourceItem) and (sourceItem['itRisk'] is not None):
        extractedData['itRisk'] = sourceItem['itRisk']
    if ('jiraPriorityId' in sourceItem) and (sourceItem['jiraPriorityId'] is not None):
        extractedData['jiraPriorityId'] = sourceItem['jiraPriorityId']
    if ('jiraPriorityName' in sourceItem) and (sourceItem['jiraPriorityName'] is not None):
        extractedData['jiraPriorityName'] = sourceItem['jiraPriorityName']
    if ('jiraProjectKey' in sourceItem) and (sourceItem['jiraProjectKey'] is not None):
        extractedData['jiraProjectKey'] = sourceItem['jiraProjectKey']
    if ('keyresults' in sourceItem) and (sourceItem['keyresults'] is not None):
        extractedData['keyresults'] = sourceItem['keyresults']
    if ('lastLoginDate' in sourceItem) and (sourceItem['lastLoginDate'] is not None):
        extractedData['lastLoginDate'] = sourceItem['lastLoginDate']
    if ('lastName' in sourceItem) and (sourceItem['lastName'] is not None):
        extractedData['lastName'] = sourceItem['lastName']
    if ('lastUpdatedBy' in sourceItem) and (sourceItem['lastUpdatedBy'] is not None):
        extractedData['lastUpdatedBy'] = sourceItem['lastUpdatedBy']
    if ('lastUpdatedDate' in sourceItem) and (sourceItem['lastUpdatedDate'] is not None):
        extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']
    if ('leanUxCanvas' in sourceItem) and (sourceItem['leanUxCanvas'] is not None):
        extractedData['leanUxCanvas'] = sourceItem['leanUxCanvas']
    if ('link' in sourceItem) and (sourceItem['link'] is not None):
        extractedData['link'] = sourceItem['link']
    if ('links' in sourceItem) and (sourceItem['links'] is not None):
        extractedData['links'] = sourceItem['links']
    if ('managerId' in sourceItem) and (sourceItem['managerId'] is not None):
        extractedData['managerId'] = sourceItem['managerId']
    if ('manWeeks' in sourceItem) and (sourceItem['manWeeks'] is not None):
        extractedData['manWeeks'] = sourceItem['manWeeks']
    if ('maxAllocation' in sourceItem) and (sourceItem['maxAllocation'] is not None):
        extractedData['maxAllocation'] = sourceItem['maxAllocation']
    if ('measurement' in sourceItem) and (sourceItem['measurement'] is not None):
        extractedData['measurement'] = sourceItem['measurement']
    if ('milestones' in sourceItem) and (sourceItem['milestones'] is not None):
        extractedData['milestones'] = sourceItem['milestones']
    if ('mmf' in sourceItem) and (sourceItem['mmf'] is not None):
        extractedData['mmf'] = sourceItem['mmf']
    if ('mvp' in sourceItem) and (sourceItem['mvp'] is not None):
        extractedData['mvp'] = sourceItem['mvp']
    if ('name' in sourceItem) and (sourceItem['name'] is not None):
        extractedData['name'] = sourceItem['name']
    if ('notes' in sourceItem) and (sourceItem['notes'] is not None):
        extractedData['notes'] = sourceItem['notes']
    if ('notificationStartDate' in sourceItem) and (sourceItem['notificationStartDate'] is not None):
        extractedData['notificationStartDate'] = sourceItem['notificationStartDate']
    if ('notificationFrequency' in sourceItem) and (sourceItem['notificationFrequency'] is not None):
        extractedData['notificationFrequency'] = sourceItem['notificationFrequency']
    if ('notStartedBy' in sourceItem) and (sourceItem['notStartedBy'] is not None):
        extractedData['notStartedBy'] = sourceItem['notStartedBy']
    if ('notStartedDate' in sourceItem) and (sourceItem['notStartedDate'] is not None):
        extractedData['notStartedDate'] = sourceItem['notStartedDate']
    if ('notStartedDateEnd' in sourceItem) and (sourceItem['notStartedDateEnd'] is not None):
        extractedData['notStartedDateEnd'] = sourceItem['notStartedDateEnd']
    if ('originSprints' in sourceItem) and (sourceItem['originSprints'] is not None):
        extractedData['originSprints'] = sourceItem['originSprints']
    if ('overrideVelocity' in sourceItem) and (sourceItem['overrideVelocity'] is not None):
        extractedData['overrideVelocity'] = sourceItem['overrideVelocity']
    if ('owner' in sourceItem) and (sourceItem['owner'] is not None):
        extractedData['owner'] = sourceItem['owner']
    if ('ownerId' in sourceItem) and (sourceItem['ownerId'] is not None):
        extractedData['ownerId'] = sourceItem['ownerId']
    if ('parentId' in sourceItem) and (sourceItem['parentId'] is not None):
        extractedData['parentId'] = sourceItem['parentId']
    if ('parentName' in sourceItem) and (sourceItem['parentName'] is not None):
        extractedData['parentName'] = sourceItem['parentName']
    if ('parentSplitId' in sourceItem) and (sourceItem['parentSplitId'] is not None):
        extractedData['parentSplitId'] = sourceItem['parentSplitId']
    if ('pendingApprovalBy' in sourceItem) and (sourceItem['pendingApprovalBy'] is not None):
        extractedData['pendingApprovalBy'] = sourceItem['pendingApprovalBy']
    if ('pendingApprovalDate' in sourceItem) and (sourceItem['pendingApprovalDate'] is not None):
        extractedData['pendingApprovalDate'] = sourceItem['pendingApprovalDate']
    if ('percentComp' in sourceItem) and (sourceItem['percentComp'] is not None):
        extractedData['percentComp'] = sourceItem['percentComp']
    if ('planningMode' in sourceItem) and (sourceItem['planningMode'] is not None):
        extractedData['planningMode'] = sourceItem['planningMode']
    if ('plannedValue' in sourceItem) and (sourceItem['plannedValue'] is not None):
        extractedData['plannedValue'] = sourceItem['plannedValue']
    if ('points' in sourceItem) and (sourceItem['points'] is not None):
        extractedData['points'] = sourceItem['points']
    if ('pointsEstimate' in sourceItem) and (sourceItem['pointsEstimate'] is not None):
        extractedData['pointsEstimate'] = sourceItem['pointsEstimate']
    if ('portfolio' in sourceItem) and (sourceItem['portfolio'] is not None):
        extractedData['portfolio'] = sourceItem['portfolio']
    if ('portfolioAskDate' in sourceItem) and (sourceItem['portfolioAskDate'] is not None):
        extractedData['portfolioAskDate'] = sourceItem['portfolioAskDate']
    if ('portfolioId' in sourceItem) and (sourceItem['portfolioId'] is not None):
        extractedData['portfolioId'] = sourceItem['portfolioId']
    if ('predecessorId' in sourceItem) and (sourceItem['predecessorId'] is not None):
        extractedData['predecessorId'] = sourceItem['predecessorId']
    if ('primaryProgramId' in sourceItem) and (sourceItem['primaryProgramId'] is not None):
        extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
    if ('priority' in sourceItem) and (sourceItem['priority'] is not None):
        extractedData['priority'] = sourceItem['priority']
    if ('priorityId' in sourceItem) and (sourceItem['priorityId'] is not None):
        extractedData['priorityId'] = sourceItem['priorityId']
    if ('processStepId' in sourceItem) and (sourceItem['processStepId'] is not None):
        extractedData['processStepId'] = sourceItem['processStepId']
    if ('processStepName' in sourceItem) and (sourceItem['processStepName'] is not None):
        extractedData['processStepName'] = sourceItem['processStepName']
    if ('productId' in sourceItem) and (sourceItem['productId'] is not None):
        extractedData['productId'] = sourceItem['productId']
    if ('productName' in sourceItem) and (sourceItem['productName'] is not None):
        extractedData['productName'] = sourceItem['productName']
    if ('productObjectiveIds' in sourceItem) and (sourceItem['productObjectiveIds'] is not None):
        extractedData['productObjectiveIds'] = sourceItem['productObjectiveIds']
    if ('products' in sourceItem) and (sourceItem['products'] is not None):
        extractedData['products'] = sourceItem['products']
    if ('program' in sourceItem) and (sourceItem['program'] is not None):
        extractedData['program'] = sourceItem['program']
    if ('programId' in sourceItem) and (sourceItem['programId'] is not None):
        extractedData['programId'] = sourceItem['programId']
    if ('programIds' in sourceItem) and (sourceItem['programIds'] is not None):
        extractedData['programIds'] = sourceItem['programIds']
    if ('programs' in sourceItem) and (sourceItem['programs'] is not None):
        extractedData['programs'] = sourceItem['programs']
    if ('prototype' in sourceItem) and (sourceItem['prototype'] is not None):
        extractedData['prototype'] = sourceItem['prototype']
    if ('quadrant' in sourceItem) and (sourceItem['quadrant'] is not None):
        extractedData['quadrant'] = sourceItem['quadrant']
    if ('rank' in sourceItem) and (sourceItem['rank'] is not None):
        extractedData['rank'] = sourceItem['rank']
    if ('readyToStartBy' in sourceItem) and (sourceItem['readyToStartBy'] is not None):
        extractedData['readyToStartBy'] = sourceItem['readyToStartBy']
    if ('readyToStartDate' in sourceItem) and (sourceItem['readyToStartDate'] is not None):
        extractedData['readyToStartDate'] = sourceItem['readyToStartDate']
    if ('reference' in sourceItem) and (sourceItem['reference'] is not None):
        extractedData['reference'] = sourceItem['reference']
    if ('region' in sourceItem) and (sourceItem['region'] is not None):
        extractedData['region'] = sourceItem['region']
    if ('regionId' in sourceItem) and (sourceItem['regionId'] is not None):
        extractedData['regionId'] = sourceItem['regionId']
    if ('regionIds' in sourceItem) and (sourceItem['regionIds'] is not None):
        extractedData['regionIds'] = sourceItem['regionIds']
    if ('regions' in sourceItem) and (sourceItem['regions'] is not None):
        extractedData['regions'] = sourceItem['regions']
    if ('regressionHours' in sourceItem) and (sourceItem['regressionHours'] is not None):
        extractedData['regressionHours'] = sourceItem['regressionHours']
    if ('release' in sourceItem) and (sourceItem['release'] is not None):
        extractedData['release'] = sourceItem['release']
    if ('releaseId' in sourceItem) and (sourceItem['releaseId'] is not None):
        extractedData['releaseId'] = sourceItem['releaseId']
    if ('releaseIds' in sourceItem) and (sourceItem['releaseIds'] is not None):
        extractedData['releaseIds'] = sourceItem['releaseIds']
    if ('releaseNumber' in sourceItem) and (sourceItem['releaseNumber'] is not None):
        extractedData['releaseNumber'] = sourceItem['releaseNumber']
    if ('releases' in sourceItem) and (sourceItem['releases'] is not None):
        extractedData['releases'] = sourceItem['releases']
    if ('releaseVehicle' in sourceItem) and (sourceItem['releaseVehicle'] is not None):
        extractedData['releaseVehicle'] = sourceItem['releaseVehicle']
    if ('releaseVehicleIds' in sourceItem) and (sourceItem['releaseVehicleIds'] is not None):
        extractedData['releaseVehicleIds'] = sourceItem['releaseVehicleIds']
    if ('reportColor' in sourceItem) and (sourceItem['reportColor'] is not None):
        extractedData['reportColor'] = sourceItem['reportColor']
    if ('requesterId' in sourceItem) and (sourceItem['requesterId'] is not None):
        extractedData['requesterId'] = sourceItem['requesterId']
    if ('revenueAssurance' in sourceItem) and (sourceItem['revenueAssurance'] is not None):
        extractedData['revenueAssurance'] = sourceItem['revenueAssurance']
    if ('revenueGrowth' in sourceItem) and (sourceItem['revenueGrowth'] is not None):
        extractedData['revenueGrowth'] = sourceItem['revenueGrowth']
    if ('riskAppetite' in sourceItem) and (sourceItem['riskAppetite'] is not None):
        extractedData['riskAppetite'] = sourceItem['riskAppetite']
    if ('riskIds' in sourceItem) and (sourceItem['riskIds'] is not None):
        extractedData['riskIds'] = sourceItem['riskIds']
    if ('risks' in sourceItem) and (sourceItem['risks'] is not None):
        extractedData['risks'] = sourceItem['risks']
    if ('roadmap' in sourceItem) and (sourceItem['roadmap'] is not None):
        extractedData['roadmap'] = sourceItem['roadmap']
    if ('roi' in sourceItem) and (sourceItem['roi'] is not None):
        extractedData['roi'] = sourceItem['roi']
    if ('role' in sourceItem) and (sourceItem['role'] is not None):
        extractedData['role'] = sourceItem['role']
    if ('roleId' in sourceItem) and (sourceItem['roleId'] is not None):
        extractedData['roleId'] = sourceItem['roleId']
    if ('roleName' in sourceItem) and (sourceItem['roleName'] is not None):
        extractedData['roleName'] = sourceItem['roleName']
    if ('scoreCardId' in sourceItem) and (sourceItem['scoreCardId'] is not None):
        extractedData['scoreCardId'] = sourceItem['scoreCardId']
    if ('shortName' in sourceItem) and (sourceItem['shortName'] is not None):
        extractedData['shortName'] = sourceItem['shortName']
    if ('schedule' in sourceItem) and (sourceItem['schedule'] is not None):
        extractedData['schedule'] = sourceItem['schedule']
    if ('scheduleType' in sourceItem) and (sourceItem['scheduleType'] is not None):
        extractedData['scheduleType'] = sourceItem['scheduleType']
    if ('score' in sourceItem) and (sourceItem['score'] is not None):
        extractedData['score'] = sourceItem['score']
    if ('score1' in sourceItem) and (sourceItem['score1'] is not None):
        extractedData['score1'] = sourceItem['score1']
    if ('score2' in sourceItem) and (sourceItem['score2'] is not None):
        extractedData['score2'] = sourceItem['score2']
    if ('score3' in sourceItem) and (sourceItem['score3'] is not None):
        extractedData['score3'] = sourceItem['score3']
    if ('score4' in sourceItem) and (sourceItem['score4'] is not None):
        extractedData['score4'] = sourceItem['score4']
    if ('scoreCardId' in sourceItem) and (sourceItem['scoreCardId'] is not None):
        extractedData['scoreCardId'] = sourceItem['scoreCardId']
    if ('self' in sourceItem) and (sourceItem['self'] is not None):
        extractedData['self'] = sourceItem['self']
    if ('short' in sourceItem) and (sourceItem['short'] is not None):
        extractedData['short'] = sourceItem['short']
    if ('shortName' in sourceItem) and (sourceItem['shortName'] is not None):
        extractedData['shortName'] = sourceItem['shortName']
    if ('snapshots' in sourceItem) and (sourceItem['snapshots'] is not None):
        extractedData['snapshots'] = sourceItem['snapshots']
    if ('solutionId' in sourceItem) and (sourceItem['solutionId'] is not None):
        extractedData['solutionId'] = sourceItem['solutionId']
    if ('source' in sourceItem) and (sourceItem['source'] is not None):
        extractedData['source'] = sourceItem['source']
    if ('spendToDate' in sourceItem) and (sourceItem['spendToDate'] is not None):
        extractedData['spendToDate'] = sourceItem['spendToDate']
    if ('sprintPrefix' in sourceItem) and (sourceItem['sprintPrefix'] is not None):
        extractedData['sprintPrefix'] = sourceItem['sprintPrefix']
    if ('sprintSchedule' in sourceItem) and (sourceItem['sprintSchedule'] is not None):
        extractedData['sprintSchedule'] = sourceItem['sprintSchedule']
    if ('startDate' in sourceItem) and (sourceItem['startDate'] is not None):
        extractedData['startDate'] = sourceItem['startDate']
    if ('startInitiationDate' in sourceItem) and (sourceItem['startInitiationDate'] is not None):
        extractedData['startInitiationDate'] = sourceItem['startInitiationDate']
    if ('startSprintId' in sourceItem) and (sourceItem['startSprintId'] is not None):
        extractedData['startSprintId'] = sourceItem['startSprintId']
    if ('state' in sourceItem) and (sourceItem['state'] is not None):
        extractedData['state'] = sourceItem['state']
    if ('status' in sourceItem) and (sourceItem['status'] is not None):
        extractedData['status'] = sourceItem['status']
    if ('storyId' in sourceItem) and (sourceItem['storyId'] is not None):
        extractedData['storyId'] = sourceItem['storyId']
    if ('strategyDate' in sourceItem) and (sourceItem['strategyDate'] is not None):
        extractedData['strategyDate'] = sourceItem['strategyDate']
    if ('strategyId' in sourceItem) and (sourceItem['strategyId'] is not None):
        extractedData['strategyId'] = sourceItem['strategyId']
    if ('strategyType' in sourceItem) and (sourceItem['strategyType'] is not None):
        extractedData['strategyType'] = sourceItem['strategyType']
    if ('strategyValue' in sourceItem) and (sourceItem['strategyValue'] is not None):
        extractedData['strategyValue'] = sourceItem['strategyValue']
    if ('strategicDriver' in sourceItem) and (sourceItem['strategicDriver'] is not None):
        extractedData['strategicDriver'] = sourceItem['strategicDriver']
    if ('strategicHorizon' in sourceItem) and (sourceItem['strategicHorizon'] is not None):
        extractedData['strategicHorizon'] = sourceItem['strategicHorizon']
    if ('strategicValueScore' in sourceItem) and (sourceItem['strategicValueScore'] is not None):
        extractedData['strategicValueScore'] = sourceItem['strategicValueScore']
    if ('tags' in sourceItem) and (sourceItem['tags'] is not None):
        extractedData['tags'] = sourceItem['tags']
    if ('targetCompletionDate' in sourceItem) and (sourceItem['targetCompletionDate'] is not None):
        extractedData['targetCompletionDate'] = sourceItem['targetCompletionDate']
    if ('targetDate' in sourceItem) and (sourceItem['targetDate'] is not None):
        extractedData['targetDate'] = sourceItem['targetDate']
    if ('targetSyncSprintId' in sourceItem) and (sourceItem['targetSyncSprintId'] is not None):
        extractedData['targetSyncSprintId'] = sourceItem['targetSyncSprintId']
    if ('team' in sourceItem) and (sourceItem['team'] is not None):
        extractedData['team'] = sourceItem['team']
    if ('teamDescription' in sourceItem) and (sourceItem['teamDescription'] is not None):
        extractedData['teamDescription'] = sourceItem['teamDescription']
    if ('teamId' in sourceItem) and (sourceItem['teamId'] is not None):
        extractedData['teamId'] = sourceItem['teamId']
    if ('teamIds' in sourceItem) and (sourceItem['teamIds'] is not None):
        extractedData['teamIds'] = sourceItem['teamIds']
    if ('teamName' in sourceItem) and (sourceItem['teamName'] is not None):
        extractedData['teamName'] = sourceItem['teamName']
    if ('teams' in sourceItem) and (sourceItem['teams'] is not None):
        extractedData['teams'] = sourceItem['teams']
    if ('teamType' in sourceItem) and (sourceItem['teamType'] is not None):
        extractedData['teamType'] = sourceItem['teamType']
    if ('testCategoryIds' in sourceItem) and (sourceItem['testCategoryIds'] is not None):
        extractedData['testCategoryIds'] = sourceItem['testCategoryIds']
    if ('testCompleteBy' in sourceItem) and (sourceItem['testCompleteBy'] is not None):
        extractedData['testCompleteBy'] = sourceItem['testCompleteBy']
    if ('testCompleteDate' in sourceItem) and (sourceItem['testCompleteDate'] is not None):
        extractedData['testCompleteDate'] = sourceItem['testCompleteDate']
    if ('testSuite' in sourceItem) and (sourceItem['testSuite'] is not None):
        extractedData['testSuite'] = sourceItem['testSuite']
    if ('testSuiteIteration' in sourceItem) and (sourceItem['testSuiteIteration'] is not None):
        extractedData['testSuiteIteration'] = sourceItem['testSuiteIteration']
    if ('themeId' in sourceItem) and (sourceItem['themeId'] is not None):
        extractedData['themeId'] = sourceItem['themeId']
    if ('themes' in sourceItem) and (sourceItem['themes'] is not None):
        extractedData['themes'] = sourceItem['themes']
    if ('throughput' in sourceItem) and (sourceItem['throughput'] is not None):
        extractedData['throughput'] = sourceItem['throughput']
    if ('tier' in sourceItem) and (sourceItem['tier'] is not None):
        extractedData['tier'] = sourceItem['tier']
    if ('timeApproverId' in sourceItem) and (sourceItem['timeApproverId'] is not None):
        extractedData['timeApproverId'] = sourceItem['timeApproverId']
    if ('timeTrackingRoles' in sourceItem) and (sourceItem['timeTrackingRoles'] is not None):
        extractedData['timeTrackingRoles'] = sourceItem['timeTrackingRoles']
    if ('timeTrackingStartDate' in sourceItem) and (sourceItem['timeTrackingStartDate'] is not None):
        extractedData['timeTrackingStartDate'] = sourceItem['timeTrackingStartDate']
    if ('timeZone' in sourceItem) and (sourceItem['timeZone'] is not None):
        extractedData['timeZone'] = sourceItem['timeZone']
    if ('title' in sourceItem) and (sourceItem['title'] is not None):
        extractedData['title'] = sourceItem['title']
    if ('trackBy' in sourceItem) and (sourceItem['trackBy'] is not None):
        extractedData['trackBy'] = sourceItem['trackBy']      
    if ('totalCapEx' in sourceItem) and (sourceItem['totalCapEx'] is not None):
        extractedData['totalCapEx'] = sourceItem['totalCapEx']
    if ('totalHours' in sourceItem) and (sourceItem['totalHours'] is not None):
        extractedData['totalHours'] = sourceItem['totalHours']
    if ('totalOpEx' in sourceItem) and (sourceItem['totalOpEx'] is not None):
        extractedData['totalOpEx'] = sourceItem['totalOpEx']
    if ('type' in sourceItem) and (sourceItem['type'] is not None):
        extractedData['type'] = sourceItem['type']
    if ('uid' in sourceItem) and (sourceItem['uid'] is not None):
        extractedData['uid'] = sourceItem['uid']
    if ('updateDate' in sourceItem) and (sourceItem['updateDate'] is not None):
        extractedData['updateDate'] = sourceItem['updateDate']
    if ('userEndDate' in sourceItem) and (sourceItem['userEndDate'] is not None):
        extractedData['userEndDate'] = sourceItem['userEndDate']
    if ('users' in sourceItem) and (sourceItem['users'] is not None):
        extractedData['users'] = sourceItem['users']
    if ('userStartDate' in sourceItem) and (sourceItem['userStartDate'] is not None):
        extractedData['userStartDate'] = sourceItem['userStartDate']
    if ('userType' in sourceItem) and (sourceItem['userType'] is not None):
        extractedData['userType'] = sourceItem['userType']
    if ('valuePoints' in sourceItem) and (sourceItem['valuePoints'] is not None):
        extractedData['valuePoints'] = sourceItem['valuePoints']
    if ('vehicleId' in sourceItem) and (sourceItem['vehicleId'] is not None):
        extractedData['vehicleId'] = sourceItem['vehicleId']
    if ('viewPublicErs' in sourceItem) and (sourceItem['viewPublicErs'] is not None):
        extractedData['viewPublicErs'] = sourceItem['viewPublicErs']
    if ('workCodeId' in sourceItem) and (sourceItem['workCodeId'] is not None):
        extractedData['workCodeId'] = sourceItem['workCodeId']
    if ('yearlyCashFlow1' in sourceItem) and (sourceItem['yearlyCashFlow1'] is not None):
        extractedData['yearlyCashFlow1'] = sourceItem['yearlyCashFlow1']
                
def ReadAllItems(which, maxToRead, filterOnProgramID=None):
    """ Read in all work items of the given type (Epic, Feature, Story, etc.) and 
        return selected fields of them to the caller.  This is NOT a complete dump of all data.
        Any work items that are deleted/in recycle bin are skipped.
    Args:
        which: Which type of work items to retrieve.  
               Valid values are: epics, capabilities, features, stories, defects, tasks
        maxToRead: Maximum number of entries to read in.
        filterOnProgramID: If not None, then check the read in item with the given
        Program ID, and skip processing it if it does not match.
    """
    print("Collecting up to " + str(maxToRead) + " items of type " + which + "...")
    itemArr = []

    # Get the first set of data, which may be everything or may not be
    if filterOnProgramID is None:
        fullUrl = cfg.instanceurl + "/" + which + "?expand=true"
    else:
        # Optimize the call by having Jira Align do the filtering
        fullUrl = cfg.instanceurl + "/" + which + "?expand=true&%24filter=programId%20eq%20" + str(filterOnProgramID)
    #print(fullUrl)

    items = GetFromJiraAlign(True, fullUrl)
    Data = items.json()
    line_count = 0
    # Starting point for skipping is to go to the next 100..
    skip = 100

    while Data != None:
        for eachWorkItem in Data:
            if 'isRecycled' in eachWorkItem:
                itemIsDel = eachWorkItem['isRecycled']
            else:
                itemIsDel = False
            # ONLY Take items that are not in the recycle bin/deleted
            if itemIsDel is True:
                continue;
            
            # If we want to filter on Program ID, then make sure it matches
            # before processing it.  If it's not processed, then it won't be
            # in the output.
            if (filterOnProgramID is not None):
                # Make sure that we don't have a case where the Program ID 
                # is specified multiple times.
                if ('programId' in eachWorkItem) and ('primaryProgramId' in eachWorkItem):
                    print("CONFLICT")
                    pass

                # Check to see if the Program we are looking at matches what we
                # are looking for.  There are two different fields that this info
                # could be in, depending on the type of item we are looking at,
                # so we have to check both.
                if ('programId' in eachWorkItem) and (eachWorkItem['programId'] != filterOnProgramID):
                    continue
                if ('primaryProgramId' in eachWorkItem) and (eachWorkItem['primaryProgramId'] != filterOnProgramID):
                    continue
                # If we get here, then the Program for this item matches what we want
                # and we should extract all the data for the item and add to the
                # result array.

            line_count += 1
            thisItem = {}
            ExtractItemData(which, eachWorkItem, thisItem)
            itemArr.append(thisItem)

        # If we got all the items, the return what we have
        if len(Data) < 100:
            break
        # If we have read in as many as request (or more) then return
        if len(itemArr) >= maxToRead:
            break

        # Otherwise, there are more items to get, so get the next 100
        if filterOnProgramID is None:
            fullUrl = cfg.instanceurl + "/" + which + "?&$skip=" + str(skip)
        else:
            fullUrl = cfg.instanceurl + "/" + which + \
                      "?expand=true&%24filter=programId%20eq%20" + str(filterOnProgramID) + "&$skip=" + str(skip)
        moreItems = GetFromJiraAlign(True, fullUrl)
        Data = moreItems.json()
        skip += 100

    print('Loaded ' + str(line_count) + " items of type " + which)
    return itemArr

def ReadOneItem(which, idToFind):
    """ Read in one work items of the given type (Epic, Feature, Story, etc.) with
        the given ID number, and return all fields of it to the caller.  
        Any work items that are deleted/in recycle bin are skipped.
    Args:
        which: Which type of work items to retrieve.  
               Valid values are: epics, capabilities, features, stories, defects, tasks
        idToFind: Search for a specific Jira Align ID number of the given type
    """
    print("Reading item of type " + which + " with ID=" + str(idToFind) + "...")
    itemArr = []
    fullUrl = cfg.instanceurl + "/" + which + "/" + str(idToFind)
    items = GetFromJiraAlign(True, fullUrl)
    eachWorkItem = items.json()
    thisItem = {}
    ExtractItemData(which, eachWorkItem, thisItem)
    itemArr.append(thisItem)

    print('Loaded ' + which + "/" + str(idToFind))
    return itemArr

def replace_non_ascii_with_spaces(text):
    """
    Scans a string and replaces all characters outside of standard ASCII (0-127) with spaces.

    Parameters:
    text (str): The input string to be processed.

    Returns:
    str: The processed string with non-ASCII characters replaced by spaces.
    """
    return ''.join([char if ord(char) < 128 else ' ' for char in text])

def replace_non_ascii_and_newlines_with_spaces(text):
    """
    Scans a string and replaces all characters outside of standard ASCII (0-127), 
    carriage returns (\r), and new line characters (\n) with spaces.

    Parameters:
    text (str): The input string to be processed.

    Returns:
    str: The processed string with non-ASCII characters, carriage returns, and new line characters replaced by spaces.
    """
    return ''.join([' ' if ord(char) >= 128 or char in ['\r', '\n'] else char for char in text])

def get_key_info(dataArray, id):
    """
    Scans the given array of objects, looking for the one with the given id, and return
    key information about it.
    
    Parameters:
    dataArray: Array of objects to scan
    id: ID number to look for
    
    Returns:
    str: The ID number and the descriptive name/title of it, if found.  An empty string
    is returned if it is not found.
    
    This function assumes that the given array has a field called 'id' in it.
    """
    tmpStr = ""
    for item in dataArray:
        if (item['id'] == id):
            tmpStr = str(item['id'])
            if 'title' in item:
                tmpStr = tmpStr + "/" + item['title']
    return tmpStr
