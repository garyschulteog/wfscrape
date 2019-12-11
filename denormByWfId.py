#!/bin/env python
import requests
import json
from collections import OrderedDict
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

WF_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v2/workforces/%s'
CE_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v1/cost_elements/%s'
POS_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v1/positions?positionGroupId=%s&workforceId=%s&start=&end='
ES_URL = "http://localhost:9200/recon4/_doc/%s"
cookies = {
    '_delphi_session': 'ADD_A_REAL_DELPHIUS_SESSION_HERE_OR_PARAMETERIZE_THIS_SCRIPT',
}

headers = {
    'content-type': 'application/json',
    'cookie': '_delphi_session=ADD_A_REAL_DELPHIUS_SESSION_HERE_OR_PARAMETERIZE_THIS_SCRIPT',
}

wfs =["0d293b3b-0b3c-49bc-8d31-5408a69a670b", "0f8f0745-a9df-4109-bf80-a07d391cb8ad", "170619b6-45ec-416d-9c0f-219a605fdb02", "1a220bf2-507e-4fa0-bbc3-5a910e9e1c63", "29e9219e-2066-4149-8945-692107ac90c7", "3fc4d6b8-42c9-4502-a9b5-e6d9f7523506", "4e2b1020-0dd0-41d9-a3f7-62926f534004", "577e02d8-1ba3-4f97-88d2-80cffda76052", "5aac3350-cf89-4a42-8708-f3b6b22d546d", "5b458915bfecce0007b2d395", "5b8eb15b60e79e0006a9bd0b", "5bef6d874b0eb10007fb8f9a", "5bf2cd164b0eb10007fb8fa6", "5c05aa534b0eb10007fba76d", "5c1076695197240007b98482", "5c17ea09fd0ca00008bf66fc", "5c19d7fb255a8500085e911d", "5c3707bdbdb1ac0008e0fff3", "5c37b764bdb1ac0008e1000c", "5c38a73bbdb1ac0008e116dd", "5c4a5d9fe1ded10008fb2e5d", "5c536706e1ded1000819c6fd", "5c59fa9577c8c200085d1dd1", "5c663750d1122900095bd7b2", "5c6cae915781c4000160938b", "5c6de1d370f4560001b9498c", "5c6ee93bcf42f40001ac3597", "5c743423e12a9d0001748b8e", "5c7eaf61e12a9d0001718f29", "5c8022b4c10f7f00018e7cac", "5c812c65c10f7f00019fcc65", "5c81419cf3b1d30001698b3e", "5c8670b8c10f7f00019fcd6b", "5c888cc6c10f7f00019fd1f1", "5c89b66da03ee40001e8bb77", "5c89b6848266a50001061e2c", "5c911d01a88f2a0001202ec7", "5c92c1e5b4b7d400011ea4bb", "5c9cc818e35f7f0001c31404", "5c9d12ef7b927f0001c84d7e", "5c9d1426e35f7f0001c3170d", "5c9e69a07b927f0001c8535e", "5cb0da9401a1700001eea5cb", "5cbf234d70e546000113dba5", "5cbf542ba356b80001cffb8e", "5cbf5b42a356b80001cffba1", "5cd06b6355dc1600014a25c2", "5cd1cf3095867600012413bc", "5cd3485294601f0001dd9ef8", "5cd4268595867600012433f9", "5cdaf14b94601f000117b7aa", "5cdda11094601f00017293bb", "5d0aa054a86c3b0018ec107d", "5d347e7af204740018b71157", "5d3b4389ab895e001863ed99", "5d3f5028f204740018b74705", "5d404d87f204740018b749cf", "5d5eebd1cae5250018010f95", "5d6698dbcae5250018011e4e", "60fbe431-fd97-4662-9976-68cfae1580d3", "61104dc7-0076-4371-bd61-732c804394c1", "6cf0a5f8-f3ac-40d1-af58-2128f8badad6", "74d35a72-df47-40b8-ac53-9da189bd84a8", "7771cd3d-325b-4f07-8def-7ae1472d436a", "79c9bfef-8e18-437c-9010-7db71f395aff", "7c2f49ee-869a-42f3-871f-36b4cb57ab23", "81079db7-1ffd-4804-b5c5-3074264abf2d", "810dc19a-1344-4ef2-ab61-eabdb6ac8c85", "899d16f9-1853-4844-adf4-be5db37c4353", "89b27342-b6a4-48a6-b9cd-a29d1669a1c6", "aa300c22-cf11-43e5-85b4-92cfcdcf18d0", "b02e33f9-7d31-411d-bbaf-d09494db9c77", "b3c9c0df-ef73-4ea7-a2a4-6614311e33f0", "bbf7c290-0314-4a3c-8cda-3a2539d19153", "d36d25fc-33ee-4f33-b0dc-f5ceab18b67f", "d413e04b-6be7-447a-8234-ff4accc77d3e", "da67c74d-d193-42d1-8072-0a4dddf87dc8", "de12d4a2-d3aa-4423-9ca4-76a2a8d6b2f3", "e6c15c8f-39fe-44de-9d0b-049222eed570", "ea3494fb-3ae7-494a-8270-5b55a202234b", "f70c989a-4de2-4fa5-8db4-ac17597b4a30", "faed4ab3-1f6d-4270-b0f0-d4c67c0f46e1", "ff2c03c7-3342-4f76-a76d-71cf8620088c"]


def requestRetry():
	session = requests.Session()
	retry = Retry(
	    total=3,
	    read=3,
	    connect=3,
	    backoff_factor=0.3,
	    status_forcelist=(500, 502, 503, 504),
	)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	return session

def main():
	errors = []
	# set wfid statically for testing
	for wfid in wfs:
		print '\twf %s' % wfid
		# get workforce skeleton def
		wf = requestRetry().get(WF_URL % wfid, headers=headers, cookies=cookies).json(object_pairs_hook=OrderedDict)['data']

        # Now load positions
		posReqGrps = []
		defPosGrpId = ""

		for pgrpidI, pgrpI in wf['configuration']['positionGroupInfo'].items():
			# get last default position group, walking forward through the ordered map
			if (pgrpI['isDefault'] == True):
				if (defPosGrpId != ""):
					# delete the prior default position group from the list (declutter the doc)
					del wf['configuration']['positionGroupInfo'][defPosGrpId]
				defPosGrpId = pgrpidI
			else:
				# save this to a list of position request groups
				posReqGrps.append(pgrpidI)					
		# add the final default position group to the list we are indexing
		posReqGrps.append(defPosGrpId)

		# now decorate the position groups with their actual position info
		for pgrpid in posReqGrps:
			resp = requestRetry().get(POS_URL % (pgrpid, wfid), headers=headers, cookies=cookies)
			if (resp.status_code >=400 and resp.status_code < 500):
				errors.append("wf: `%s` pgrp: `%s` message: `%s`" % (wfid, pgrpid, resp.json()['message']))
			elif (resp.status_code >= 500): 
				errors.append("wf: `%s` pgrp: `%s` code: %d" % (wfid, pgrpid, resp.status_code))
			else:
				# update workforce with positions
				for pos in resp.json()['data']:
					posId = pos['_id']
					wf['configuration']['positionGroupInfo'][pgrpid]['positionsInfo'][posId] = pos

        # Now load Cost Elements
		wf['wfid'] = wf.pop('_id')
		for ce, blah in wf['configuration']['costElementsInfo'].items():
		#	print ce
			if (ce != 'costElements'):
				resp = requestRetry().get(CE_URL % ce, headers=headers, params={'workforceId':wfid}, cookies=cookies)
				if (resp.status_code == 200):
					#update workforce
					wf['configuration']['costElementsInfo'][ce] = resp.json(object_pairs_hook=OrderedDict)['data']
				elif (resp.status_code >=400 and resp.status_code < 500):
					errors.append("wf: %s ce: %s message: %s" % (wfid, ce, resp.json()['message']))
				else: 
					errors.append("wf: %s ce: %s code: %d" % (wfid, ce, resp.status_code))



		resp = requests.post(ES_URL % wfid, headers={'content-type': 'application/json'}, data=json.dumps(wf, indent=4))
		print '\t\tresponse: %s' % resp.status_code

	for error in errors:
		print error
main()


