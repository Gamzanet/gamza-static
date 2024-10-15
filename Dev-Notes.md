## TO-DO

- [x] Add Foundry Projects as modules
    - `git submodule add https://github.com/ooMia/v4-template foundry/v4-template`
    - `git submodule add https://github.com/ooMia/Upside_Cookie_Land foundry/cookie`

- [x] Verify on-chain deployed Hook source
    - use `0x7d61d057dD982b8B0A05a5871C7d40f8b96dd040` initialized on
      tx `0x51bf9fdd076d4076212562d50caf012fccc7efc3a10e93efb358c30e08855f0a` in unichain
       ```markdown
       # (address,address,uint24,int24,address hookAddress) key
       ("0x0000000000000000000000000000000000000000",
       "0x6f0cd9ac99c852bdba06f72db93078cba80a32f5",
       "0",
       "60",
       "0x7d61d057dd982b8b0a05a5871c7d40f8b96dd040")
       # uint160 sqrtPriceX96
       79228162514264337593543950336
       # bytes hookData
       0x
       ```

- [x] RPC로 해당 컨트랙트 및 의존성 소스를 모두 저장
    - `lib/etherscan/unichain:store_all_dependencies()` 참조

- [x] forge fmt 포맷팅
    - `lib/parser/layer0:format_code()`

- [x] ~~소스 수준에서 Hook Source에 한해서만 solHint Linting~~

- [x] 기본 [semgrep solidity rules](https://github.com/semgrep/semgrep-rules/tree/develop/solidity) & custom rule
    - LLM 명제를 분해하여 rule로 추가

- [x] Slither 추가 → compile하여 linting 결과 → 규칙 형태로 관리

- [x] ~~Hook validation without BaseHook~~

- [ ] slither on Layer2 - call graph & contract dependency graph

- [ ] LLM analysis
