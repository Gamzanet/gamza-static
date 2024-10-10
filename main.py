import etherscan.ether_api_call as eac

if __name__ == "__main__":
    res = eac.get_source_from_etherscan("0xe8e23e97fa135823143d6b9cba9c699040d51f70")
    print(res)

    # res = is_valid_hook(_target_path="code/1.sol")
    # res: dict = get_modifiers(_target_path="code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol")
    # for k, v in res.items():
    #     print(k, v)
    # print(os.curdir)
    # res = get_variables(_target_path="code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol")
    # pprint(res)
