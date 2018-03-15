# API文档

## 0.排名功能
/api/rankings/aoapcs
/api/rankings 总题数排名
{
    data: {
        rankings: [
        {
            user:
            realName:
            count:
        }
        ]
        oj: {
            oj_name:""
        }
    }
}
## 0.功能需求
list:
用户各OJ数
detail:
用户OJ详细
## 1. 解决题目
```json
{
    id:
    user:
    oj_names: {'oj_name1', ..}
    solved: {
        'oj_name1': oj_count1,
        ...
    }
}
```
## 2. 解决题目详细信息
### 1. 所有OJ解决详细信息 /api/solved
```json
{
    id:
    user:
    solved: {'oj_name1': ['p1', 'p2',...],
          'oj_name2': ...
        }
    oj_names: {'oj_name1', ..}
}
```
### 2. 特定OJ/专题集/书解决详细情况 /api/solved/uva
{
    user: sdkjdxwzh
    total: 1254
    data: {
        ojs:{
        'oj_name' : "aoapc_guide",
        'cnt': 111
         chaps:[{
            chap: "chap1",
            solved_cnt: "",
            solved: []
        },],
        'oj_name' : "aoapc_guide",
        'cnt': 111
         chaps:{
            chap: "chap1",
            solved_cnt: "",
            solved: []
        },
    }
    }
    oj_name:
}
```json
{
    user:
    solved: {'chap1\volumn1': ['p1', 'p2',...],
          'chap2': ...
        }
    oj_name: 'oj_name'
}
```
## 3. 题目信息
查看某OJ详细信息 /api/problems/uva
```json
{
    oj: 'oj_name'
    problems: {
        'chap1\volumn1': ['p1', 'p2', 'p3', ...],
        'chap2\volumn2': ['p1', 'p2', 'p3']
    }
}
查看某题目详细信息 /api/problems/uva/id
```
json格式：
```json
{
   id:
   oj_name:
   problem_id:
   title:
   label:
   status:{
      ac:
      wa:
      pe:
   }
}
```
- api/problems/uva 查看uva题目信息
- api/problems 查看所有题目信息