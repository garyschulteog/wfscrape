#!/bin/env python
import requests
import json
from collections import OrderedDict
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

WF_LIST_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v2/workforces?entityId=%s'
#WF_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v2/workforces/%s'
CE_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v1/cost_elements/%s'
CE_LIST_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v1/cost_elements?workforceId=%s&start=&end='
POS_URL = 'https://controlpanel.opengov.com/api/wf_dataset_service/v1/positions?positionGroupId=%s&workforceId=%s&start=&end='
ES_URL = "http://localhost:9200/renorm/_doc/%s"
cookies = {
    '_delphi_session': '_I_NEED_A_DELPHIUS_KEY'
}

headers = {
    'content-type': 'application/json',
    'cookie': '_delphi_session=_I_NEED_A_DELPHIUS_KEY'
}

wf_entities =[2918 ,2805 ,2728 ,2413 ,2698 ,2796 ,2732 ,2881 ,2786 ,2753 ,291 ,2880 ,2908 ,
1937 ,906 ,115 ,2410 ,73 ,52 ,226 ,123 ,2645 ,2788 ,2279 ,136 ,61 ,211 ,2932 ,1308 ,2863 ,
257 ,2701 ,243 ,2521 ,2978 ,2334 ,2792 ,252 ,2669 ,2056 ,2878 ,2595 ,688 ,823 ,2995 ,333 ,
270 ,2107 ,319 ,2933 ,2313 ,651 ,1843 ,2877 ,491 ,2821 ,1199 ,662 ,2273 ,2943 ,1490 ,1886 ,
1224 ,2822 ,790 ,2042 ,2381 ,1554 ,2879 ,1864 ,2191 ,2937 ,2806 ,2917 ,2816 ,630 ,2522 ,2740 ,
2794 ,2751 ,2731 ,2871 ,2537 ,925 ,2373 ,2719 ,2707 ,2371 ,2710 ,1717 ,1754 ,1051 ,2770 ,396 ,
1237 ,2942 ,1653 ,2741 ,2931 ,1887 ,2886 ,2523 ,2287 ,2425 ,560 ,2362 ,2703 ,1918 ,2811 ,2729 ,
2614 ,2153 ,2993 ,1352 ,267 ,2530 ,2977 ,2772 ,2745 ,2944 ,2440 ,2897 ,2876 ,2607 ,2920 ,765 ,
757 ,466 ,2940 ,2935 ,3007 ,2594 ,2921 ,2325 ,2771]


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
	for entity_id in wf_entities:
		print "entity %s" % entity_id
		wfs = requestRetry().get(WF_LIST_URL % entity_id, headers=headers, cookies=cookies).json(object_pairs_hook=OrderedDict)['data']
		for wf in wfs:
			wfid = wf['_id']
			print '\twf %s' % wfid
			wf['wfid'] = wf.pop('_id')
	        
			# Now load cost elements
			newCes = []

			resp = requestRetry().get(CE_LIST_URL % wfid, headers=headers, cookies=cookies)
			if (resp.status_code >= 500):
				errors.append("entity: `%d` wf: `%s` ce: `%s` code: %d" % (entity_id, wfid, ce, resp.status_code))				
			elif (resp.status_code >=400 and resp.status_code < 500):
				errors.append("entity: `%d` wf: `%s` ce: `%s` message: `%s`" % (entity_id, wfid, ce, resp.json()['message']))
			else: 
				for ce in resp.json()['data']:
					ceId = ce['_id']
					newCes.append(ce)

			#rewrite workforce with list of cost elements
			del wf['configuration']['costElementsInfo'] 
			wf['configuration']['costElementsInfo'] = newCes

	        # Now load positions
			posReqGrps = []
			defPosGrp = {}

			for pgrpidI, pgrpI in wf['configuration']['positionGroupInfo'].items():
				# get last default position group, walking forward through the ordered map
				if (pgrpI['isDefault'] == True):
					defPosGrp = pgrpI
				else:
					# save this to a list of position request groups
					posReqGrps.append(pgrpI)					
			# add the final default position group to the list we are indexing
			posReqGrps.append(defPosGrp)

			# remove the positionGroups map and replace with an array
			del wf['configuration']['positionGroupInfo']
			posGrps = []

			# now decorate the position groups with their actual position info
			for pgrp in posReqGrps:
				if (pgrp.has_key('_id')):
					resp = requestRetry().get(POS_URL % (pgrp['_id'], wfid), headers=headers, cookies=cookies)
					if (resp.status_code >=400 and resp.status_code < 500):
						errors.append("entity: `%s` wf: `%s` pgrp: `%s` message: `%s`" % (entity_id, wfid, pgrp['_id'], resp.json()['message']))
					elif (resp.status_code >= 500): 
						errors.append("entity: `%s` wf: `%s` pgrp: `%s` code: %d" % (entity_id, wfid, pgrp['_id'], resp.status_code))
					else:
						# update workforce with positions
						positions = []
						for pos in resp.json()['data']:
							posId = pos['_id']
							positions.append(pos)
						#rewrite as a list of positions
						del pgrp['positionsInfo']
						pgrp['positionsInfo'] = positions

					posGrps.append(pgrp)

			#rewrite this as a list of positiongroups
			wf['configuration']['positionGroupInfo'] = posGrps

			#dump the doc we are about to index
			#print json.dumps(wf, indent=4, separators=(',', ': '))

			resp = requests.post(ES_URL % wfid, headers={'content-type': 'application/json'}, data=json.dumps(wf, indent=4))
			print '\t\tresponse: %s - %s' % (resp.status_code, resp.content)

	for error in errors:
		print error

main()


