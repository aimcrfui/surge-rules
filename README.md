# Surge 个人规则与本地模块服务

这个项目维护两类内容：

- `rules/*.list`：可发布到 GitHub Raw 的个人 Surge 分流规则。
- `modules/*.sgmodule`：需要本地静态服务配合安装的 Surge 模块。

## GitHub 规则引用

把下面片段放到主配置 `[Rule]` 中，并且放在大型公开规则前面：

```ini
RULE-SET,https://raw.githubusercontent.com/aimcrfui/surge-rules/main/rules/reject.list,REJECT
RULE-SET,https://raw.githubusercontent.com/aimcrfui/surge-rules/main/rules/direct.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/aimcrfui/surge-rules/main/rules/ai.list,AIGC
RULE-SET,https://raw.githubusercontent.com/aimcrfui/surge-rules/main/rules/stream.list,Stream
RULE-SET,https://raw.githubusercontent.com/aimcrfui/surge-rules/main/rules/proxy.list,Foreign
```

完整片段也在 [surge-rule-snippet.conf](/Users/ccoo/Projects/surge/surge-rule-snippet.conf)。

## 自动更新

[update-rules.yml](/Users/ccoo/Projects/surge/.github/workflows/update-rules.yml) 每 24 小时运行一次，也可以在 GitHub Actions 手动触发。它会执行：

```bash
python3 scripts/update_rules.py
```

生成器会读取 [sources/providers.json](/Users/ccoo/Projects/surge/sources/providers.json)，拉取上游规则，再输出到 `rules/`。如果生成结果没有变化，workflow 不会提交空更新。

## 个人 override

不要直接编辑 `rules/*.list`。把自己的规则写到 `personal/*.list`，再运行生成器。

示例：

```ini
# personal/direct.list
DOMAIN-SUFFIX,example.cn

# personal/proxy.list
DOMAIN-SUFFIX,example.com

# personal/reject.list
DOMAIN-SUFFIX,analytics.example.com
```

注意：GitHub Raw 规则仓库如果是公开仓库，个人域名也会公开。敏感域名建议继续保留在本地 profile，不要放到 `personal/*.list` 后推送。

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

如果改用其他端口，例如 `8000`，需要同步修改 [PROMPT.md](/Users/ccoo/Projects/surge/PROMPT.md) 里的 `【本地模块服务地址】`。
