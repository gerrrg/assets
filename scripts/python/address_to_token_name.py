# @author gerg
# @brief get token caps by token name/symbol

import etherscan
import json
import time
import os

# inputs/parameters
api_key = 'ADD_YOUR_API_KEY_HERE';
eligible_tokens_path = "../../lists/eligible.json";
verbose = True;

# define output file path
output_path_elements = os.path.split(eligible_tokens_path);
output_file_elements = output_path_elements[1].split('.')
output_file_elements[0] += '_by_symbol';
output_file = '.'.join(output_file_elements)
output_path = os.path.join(output_path_elements[0], output_file)

if verbose:
	print("API Key:", api_key);
	print("Eligible Tokens Path:", eligible_tokens_path);
	print("Output Path:", output_path)

# etherscan API throttles to 5Hz
max_queries_per_sec = 5.0;
time_per_request = 1.0/max_queries_per_sec + 0.1;

# read eligible tokens to dict
eligible = None;
with open(eligible_tokens_path) as json_file:
    eligible = json.load(json_file)

out_dict = {};
for network in eligible.keys():
	
	# mainnet/testnet tokens
	network_name = network;

	# etherscan API expects mainnet specifier to be None
	if network_name=="homestead":
		network_name=None;
	
	# connect to etherscan API for specific network
	es = etherscan.Client(
		network=network_name,
	    api_key=api_key,
	    cache_expire_after=max_queries_per_sec,
	)

	# get all whitelisted token addresses for current network
	token_addresses = (eligible[network].keys())

	# get all token names and symbols for each token address
	network_dict = {};
	for curr_address in token_addresses:
		token_transations = es.get_token_transactions(
		    contract_address=curr_address, limit=1
		)
		# extract name, symbol from etherscan
		token_name = token_transations[0]['token_name'];
		token_symbol = token_transations[0]['token_symbol'];
		
		# get cap from eligible.json
		cap = eligible[network][curr_address];

		# populate dict
		value = (token_symbol, token_name, cap)
		network_dict[curr_address] = value;

		# optional print to see outputs as it runs
		if verbose:
			print("\t", network, value)

		time.sleep(time_per_request)

	out_dict[network] = network_dict

if os.path.exists(output_path):
  os.remove(output_path)
  if verbose:
  	print("Deleted existing", output_path)

with open(output_path, 'w') as fp:
    json.dump(out_dict, fp, indent=4)
