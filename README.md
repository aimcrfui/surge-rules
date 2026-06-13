# Personal Surge Rules

这个仓库维护个人 Surge 覆盖规则、有序的完整 `[Rule]` 模板，以及本地 Surge 模块。

- `rules/personal/non_ip/*.list`：个人域名、进程、端口和逻辑规则。
- `rules/personal/ip/*.list`：个人 IP 规则。
- `surge-rule-snippet.conf`：按正确顺序组织个人规则和 Sukka 上游规则的完整模板。
- `modules/*.sgmodule`：需要本地静态服务配合安装的 Surge 模块。

## 设计原则

- 个人明确指定的规则优先于上游规则。
- 所有非 IP 规则位于会触发 DNS 解析的 IP 规则之前。
- `stream/global` 位于 `domestic` 之前。
- Sukka 上游规则由 Surge 直接引用，不在本仓库重新合并。
- 最后使用 `FINAL,Foreign,dns-failed`。

完整顺序和原因见 [docs/rule-order.md](docs/rule-order.md)。

## 使用

将 [surge-rule-snippet.conf](surge-rule-snippet.conf) 中的 `[Rule]` 替换进主配置。模板使用当前个人策略组：

- `in`
- `Home`
- `Foreign`
- `AIGC`
- `Stream`
- `Telegram`

如果策略组改名，必须同步修改模板。

## 添加个人规则

根据目标策略编辑对应文件：

- 永远直连：`rules/personal/non_ip/direct.list`
- 国内网络感知策略：`rules/personal/non_ip/in.list`
- 海外默认策略：`rules/personal/non_ip/foreign.list`
- AIGC、流媒体、Telegram：对应同名文件
- IP 规则：放入 `rules/personal/ip/` 的对应文件

外部规则集中的每一行不能包含策略名。个人 IP 规则只想匹配已经是 IP 地址的连接时，应添加 `no-resolve`。

示例：

```ini
# rules/personal/non_ip/in.list
DOMAIN-SUFFIX,example.cn

# rules/personal/non_ip/foreign.list
DOMAIN-SUFFIX,example.com

# rules/personal/ip/direct.list
IP-CIDR,100.64.0.0/10,no-resolve

# rules/personal/non_ip/reject.list
DOMAIN-SUFFIX,analytics.example.com
```

提交前运行：

```bash
python3 scripts/validate_rules.py
python3 scripts/check_upstreams.py
```

GitHub Actions 每 24 小时执行相同检查。Sukka 网站分类规则由 Surge 直接读取上游 URL，因此无需在本仓库复制更新。敏感域名不要提交到公开仓库。

## 本地模块服务

`5500` 不是系统自带端口，只是本项目约定的静态服务端口。Surge 安装直链要可用，必须先从当前项目目录启动一个 HTTP 静态文件服务。

推荐从本目录启动：

```bash
cd /Users/ccoo/Projects/surge
python3 -m http.server 5500 --bind 0.0.0.0
```

启动后，模块直链格式为：

```text
http://192.168.1.63:5500/modules/example.com.sgmodule
```

如果改用其他端口，例如 `8000`，需要同步修改 [PROMPT.md](PROMPT.md) 里的 `【本地模块服务地址】`。
