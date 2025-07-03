# Ludus Range Builder

An interactive Python script to generate Ludus range definitions with:

- Default attacker VLAN 99 setup (Kali, Windows attack, TeamServers, Redirectors)  
- Dual YAML output:  
  - `*_build.yml` (open networking)  
  - `*_segmented.yml` (strict VLAN isolation + special allow rules)  
- Final menu to save, load into Ludus, deploy & watch, or discard  

---

## 🏃‍♂️ Quickstart

1. Install prerequisites:
```bash
pip install pyyaml jinja2
```
2. Place `range_builder.py` alongside your `ludus_forest_build_roles` repo.
3. Run:
```bash
python3 range_builder.py --range-id 10
```
4. Follow the prompts:
- Include default attacker setup? (Y/n)
- How many TeamServers? (1/2)
- How many Redirectors? (1/2)
5. At the end, choose:
```yaml
1) Save YAML only  
2) Save + `ludus range config set`  
3) Save + load + `ludus range deploy` + `watch -c "ludus range list"`  
4) Discard and exit  
```
Your two files will be:
- `range_build.yml`  
- `range_segmented.yml`  

---

## ✨ Features & Edge-Cases

- **Fast templating** via Jinja2  
- **PyYAML** for valid YAML dumps  
- **Interactive validation** for numeric inputs  
- **Network policy** section in segmented output  
- **Stubs** for adding domain-related VMs manually or via future enhancements  
- **Smart defaults** for IP addressing: `10.<range_id>.99.xxx`  

---

## 🔧 Customization

- Edit the `OPEN_TEMPLATE` and `SEGMENTED_TEMPLATE` strings to adjust YAML structure.  
- Expand `build_default_attackers()` to tweak attacker VM specs.  
- Add domain-VM prompts under the “TODO” section in `main()`.  

---

## 📎 License

MIT © H4cksty
