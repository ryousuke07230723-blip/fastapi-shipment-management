print("""
apiとはパソコンとDB(データベース)の間にある橋渡し役
restとはルール、ガイドラインで,api restがapiのルールuriとは,ほぼurlと同じ意味、インターネット上の住所

Endpointとは、apiが受け取る目的地の名前
uriとendpointを合わせてurlになる     
HTTPとはrestを荷物としてapiまで運ぶレール、共通の言語を使ってデータを送信する(メソッドはHTTPが用意してる)

送るはpost 情報もらうだけならget
Headerは注文に載せる付加情報(私の身分証はこれ)
Bodyは相手に送りたいメインのデータ 
これらとurlをまとめて送る(post)
postとgetの違いは、注文票をただ見せて欲しいか、自分の情報を送って記録にペンで書き換えること、つまりいじるということ

200代は成功
300はもう一度送信して
400はクライアント側に問題あり
500はサーバー側に問題あり

これらのrest(ルール)に従ったAPI設計はrestfulと言う       
""")

print("""
FastAPIについて
FastAPIとはサーバー本体、リクエストを待ち受けているレストラン
@とはデコレータ、強制的にその関数に案内する係,これがお客さんが入力した情報の中に@ooo('/menu)これがあったら関数に案内しますという役割
defとは関数、データを作る料理人
これがバックエンドの仕組み
      
FastAPIが人気な理由
1 ユーザーが余計な情報も入力してしまっても自動で必要な情報だけを取り出す　name:str price:int
2 勝手にでどんなデータが必要で何が返ってくるかの説明書を作ってくれる 他のエンジニアにurlを渡すだけでいい
3 あらかじめ用意しておくとすぐに情報を渡してくれる　弁当に割り箸をつけてくれるみたいに
4 並行処理が可能　同時に大量のリクエストを捌くことができる

：豆知識
FastAPIは元々存在していた2つのものを組み合わせたもの
1 Starlette(スターレット)：通信を受け取り案内する速度が早い案内役
2 Pydantic(パイダンティック)：データを正確かどうか見抜く専門家
      
Fastapiはwebフレームワーク(処理担当)でuvicornがwebサーバー(通信担当)というふうに常に2人1組で動いている
uvicornという店長がHTTPで送られてきた言語をPythonにして、FastAPIの厨房スタッフがデータの処理を行う
uvicorn app:app --reload　よく打つこのコードの意味も、uvicornにapp.pyというファイルの中にあるapp = fastapi()以降のコードの処理を行って自動で更新してという命令
""")

print("""
raiseはreturnの反対版、エラーを発生させる役割
@getはデータを取得する役割
@postは新しくデータを作る役割
@putはデータを更新する役割

field(lt(less_than)=25)は25未満
field(le(less_equal)=25)は25以下  
field(ge(greater_equal)=25)は25以上
field(gt(greater_than)=25)は25より大きい
field(max_length=25)は25文字以下
field(min_length=25)は25文字以上
descriptionは説明文
      
FastAPI上だと型ヒントもBaseModelも両方とも拘束力を持っている、
型ヒントはurlなどの一つの小さなデータを扱う
BaseModelは複数のデータをまとめて扱う、例えばユーザーの名前と年齢と住所をまとめて扱うなど
Enumは選択肢を決めるところ、例えばユーザーの性別を男、女、その他から選ぶなど
      

SQLはデータベースを操作するための言語、SQLAlchemyはPythonでSQLを扱うためのライブラリ
データベースのメソッド
INSERT 作成
SELECT 読み取り
UPDATE 更新
DELETE 削除 
DROP テーブルの削除
CREATE テーブルの作成
      
(id,)この,の意味は情報が複数入ってくるよということ id, status, content
'id :idは新しくして欲しいと持ってこられたidをいれて古いidを上書きしてるという意味
**shipment.model_dump()は分解して{id,status,count}という1まとまりにしようということ    

get_args 型ヒントの中をタプルで返してくれる、つまり(   ,   ,) こういうこと
      """)
print("""
基本知識
関数とは単独で動く処理,def ooooo
クラスとは設計図,class
メソッドはクラスの中にある関数のこと

色の違い
紫(from,import,return,def,with,yield)
Pythonの絶対ルール、自分では作れないもの、最初からPythonにあるもの
      
黄色(create_engine(),   getsession()   )
動詞、アクション（関数、メソッド)
何かの処理を実行する命令
      
緑(SessionDep,SQLModel,Session,shipment)
クラス、設計図、型

水色(engine,fastAPI,session)
変数、モジュールなどの一時的に何かを入れておく箱
      
オレンジ('あいおじじj')
ただの文字
      
暗い緑
#説明、メモ
      
refresh:データベースの最新情報を取り寄せてこっちのデータを上書きする
session.refresh(new_shipment)：sessionの持ってるnew_sipmentの情報を最新にして

APIスキーマは入り口でのチェック係:pydantic
class user(BaseModel)
DBのことは一切知らない、関係ない、
客が渡してくる情報をAPIエンドポイント付近で検査する

SQLModelはDBに保存される形を決める、検査係
class user(SQLModel,table=True)のやつ
奥側での保存担当、テーブルの形を定義する

APIスキーマ(Pydantic)とSQLModelを合体して1つの簡潔なコードにすることもできる
この場合PydanticにSQLmodelを継承させる形になるから基板がPydanticとかんがえてたらいい
しかし、2つにすることによってDBへの壁がなくなりクライアントとDBが近くなるからあまり良くない方法
基本は2つに分けて作る
      
非同期処理(並行処理)
asyncioを使う、外部との通信,待ち時間が必要な処理 DBへの接続も
同期処理、つまり待たないといけない行動(メソッド)などの前にawaitを置かないといけない
for文などで並列処理を行う時、その処理が全て終わるまでwaitで待ってあげないといけない(1クッション必要)
with構文を使うとそのワンクッションの待つ作業は自動でしてくれる
      
option+クリックで選択してまとめて置き換え

本部は@appそれ以外の分けたところは@router
毎回__init__.pyを作る理由：これがないとpythonのプログラム部品が入ってると認識してくれない
中身は空っぽで良い、pythonの部品箱ですという目印、ないと写真やメモのファイルとして認識される

-> Shipment：わざわざクラスで返す理由はこのクラスの中でcount:strのように定義されたもの、それ以外の情報は入ってこないようにするため

同じクラス内のメソッドを呼ぶときはメソッドの前にself.getのようにselfが必要
OOO(△△△△△)はOOOに△△△△△を渡す、 OOが主役

app = FastAPI()
router = APIRouter()
右の2つはfastapiに備わってる機能で実行したらEndpointの(@get,post)など、登録できるようになる
左はただの変数箱、他のとこでこの場所で書いたコードと繋げたいとき、
      
複数のルートで使いたいものを依存性注入にする
_は使わない等意味

Redis内部のイメージ（辞書みたいなもの）：
{
    "abc123(JWTのjit)" : "blacklisted",
    "xyz789(JWTのjit)" : "blacklisted",
}

jti(ログアウト)の動きの確認

1:"jti": str(uuid4())これでuserに渡すトークンのjtiを潜ませておく

2:ログアウトしたいと要望が来る
token_data: Annotated[dict, Depends(get_access_token)]
     token_data["jti"]
トークンを長い文字列からjson形式の{}の形に戻す
中にあるjtiだけ引っこ抜く

3:jtiをRedisに登録する(ログアウトされたものが登録される場所blacklist)
await _token_blacklist.set(jti, "blacklisted")

4:次回からはそのトークンで引き続き入ってこようとしてもログアウトしたら無理

UUID 型のルール: 〇〇-〇〇-〇〇-〇〇-〇〇 という、ハイフンで繋がれた36文字の特定の形しか絶対に入らない！
Relationshipが架け橋

      
リビジョンスクリプト = 「DBへの工事指示書」
migrations/
  versions/
    1c2c85e7b996_add_shipment_table.py   ← これがリビジョンファイル
    5b6a1d4383b6_add_destination_column.py
      
データを見る・確認する,手動で修正するなどはDBを直接tabluplusなどのアプリから触る方が向いているが、
      テーブルの構造を変えるなどはAlembicを使ってターミナルから間接的にDBを触る方が向いている、理由は記録が残るから

Fieldの中身
DBのテーブル構造に関わる？
  ├── Yes（primary_key, sa_column など）→ 継承NG
  └── No（exclude, description など）  → 継承OK






""")
