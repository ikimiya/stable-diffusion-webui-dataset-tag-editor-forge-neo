# Dataset Tag Editor Neo

[toshiaki1729/stable-diffusion-webui-dataset-tag-editor](https://github.com/toshiaki1729/stable-diffusion-webui-dataset-tag-editor) のフォークで、[Haoming02/sd-webui-forge-classic](https://github.com/Haoming02/sd-webui-forge-classic)（neoブランチ）との互換性のために更新されました。

[SD WebUI Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic) のトレーニングデータセットのキャプションを編集する拡張機能です。

画像ファイル名のキャプションは読み込めますが、編集したキャプションはテキストファイルとしてのみ保存できます。

## インストール
### WebUIの拡張機能タブから
1. Forge-Neoで **Extensions → Install from URL** を開く
2. 以下を貼り付ける: `https://github.com/ikimiya/stable-diffusion-webui-dataset-tag-editor-forge-neo`
3. Installをクリックし、Apply and restartを行う

**「Extensions」タブからこの拡張機能を更新した場合、完全に再読み込みするためにWeb UIを再起動する必要があります。**

### 手動インストール
リポジトリを `extensions` ディレクトリにクローンしてWeb UIを再起動してください。

```commandline
git clone https://github.com/ikimiya/stable-diffusion-webui-dataset-tag-editor-forge-neo extensions/dataset-tag-editor
```

> Forge-Neo（neoブランチ）・Gradio 4.40.0・Python 3.13.12 にて動作確認済み

## 新機能

### タグインプリケーション
データセット全体の関連タグを整理するための新しいタブです。

![](pic/tab01.png)

**使い方:**
1. **Scan Dataset** をクリックしてタグを読み込む
2. 親タグを選択 — 例: `skirt (17)`
3. **追加** するタグにチェックを入れる — 例: `white skirt (7)`、`pleated skirt (4)`
4. **削除** するタグにチェックを入れる — 例: `shorts under skirt (2)`
5. 必要に応じてカスタムタグを追加 — 例: `miniskirt, grey skirt`
6. **Apply** をクリック

![](pic/tab03.png)

適用後、`skirt` を持つ17枚の画像すべてに `white skirt`、`pleated skirt`、`miniskirt`、`grey skirt` が追加されます。親タグはデフォルトで削除されます。

他のタブでタグを編集した場合は、**Scan Dataset** を再度クリックしてカウントを更新してください。

> **Tag Autocomplete について**
> カスタムタグ入力欄でオートコンプリートを有効にするには、以下のファイルを開いてください:
> `extensions\a1111-sd-webui-tagcomplete\javascript\_textAreas.js`
>
> `dataset-tag-editor` のセレクターセクション（約20行目）に以下の2行を追加してください:
> ```javascript
> "dataset-tag-editor": {
>     "base": "#tab_dataset_tag_editor_interface",
>     "hasIds": false,
>     "selectors": [
>         "Caption of Selected Image",
>         "Interrogate Result",
>         "Edit Caption",
>         "Edit Tags",
>         "Add custom tags to add (comma-separated)",
>         "Add custom tags to delete (comma-separated)",
>     ]
> },
> ```

## オリジナルからの変更点

**Forge-Neo / A1111 互換性**
- `lowvram` モジュールを削除 — Forge-Neoが自動でメモリ管理を行うため
- `ldm` インポートを削除 — 不要のため
- A1111の `sd_hijack.py` をローカルコピーとして追加 — `modules.sd_hijack` が存在しないため
- `compat.py` を追加 — 起動時に不足している `shared.opts` 設定をデフォルト値でパッチ
- `shared.cmd_opts.use_cpu` の参照を修正
- `shared.sd_model.cond_stage_model` にnullガードを追加 — Flux・Animaなどの新しいアーキテクチャでは単語分割にフォールバック
- `DeepDanbooru` タガーを削除 — Forge-Neoでは使用されていないため
- `read_wd_batchsize` の不足していた大型タガー（`wd-eva02-large`・`wd-vit-large` など）を修正
- `WD_TAGGERS_TIMM` の不足していたタガーエントリを復元

**Gradio 4 互換性**
- 入力バリデーションエラーを修正するため、インスタンスメソッドのコールバックをラムダでラップ

**依存関係**
- `install.py` を追加 — 起動時に `open-clip-torch` を自動インストール

## 既知の制限事項
- DeepDanbooruタガーは無効 — WD14またはEVA-02を使用してください
- トークンカウンターは正確なCLIPトークンではなく単語分割を使用

---

*AIによる翻訳*

# Dataset Tag Editor
[**スタンドアロン版はこちらです**](https://github.com/toshiaki1729/dataset-tag-editor-standalone): いくつかの既知のバグを回避するのに有効かもしれません。


[English Readme](README.md)

[Stable Diffusion web UI by AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)用の拡張機能です。

web UI 上で学習用データセットのキャプションを編集できるようにします。

![](ss01.png)

DeepBooru interrogator で生成したような、カンマ区切り形式のキャプションを編集するのに適しています。

キャプションとして画像ファイル名を利用している場合も読み込むことができますが、保存はテキストファイルのみ対応しています。

## インストール方法
### WebUIのExtensionsタブからインストールする
"Install from URL" タブに `https://github.com/toshiaki1729/stable-diffusion-webui-dataset-tag-editor.git` をコピーしてインストールできます。  
"Availables" タブにこの拡張機能が表示されている場合は、ワンクリックでインストール可能です。  
**web UI の "Extensions" タブから更新をした際、完全に更新を適用するには web UI を再起動する必要がある場合があります。**  

### 手動でインストールする
web UI の `extensions` フォルダにリポジトリのクローンを作成し再起動してください。

web UI のフォルダで以下のコマンドを実行することによりインストールできます。
```commandline
git clone https://github.com/toshiaki1729/stable-diffusion-webui-dataset-tag-editor.git extensions/dataset-tag-editor
```

## 特徴
以下、「タグ」はカンマ区切りされたキャプションの各部分を意味します。
- テキスト形式（webUI方式）またはjson形式 ([kohya-ss sd-scripts metadata](https://github.com/kohya-ss/sd-scripts))のキャプションを編集できます
- 画像を見ながらキャプションの編集ができます
- タグの検索ができます
- 複数タグで絞り込んでキャプションの編集ができます
  - 絞り込み方法として、AND/OR/NOT検索ができます
- タグを一括で置換・削除・追加できます
- タグを一括で並べ替えできます
- タグまたはキャプション全体について一括置換ができます
  - [正規表現](https://docs.python.org/ja/3/library/re.html#regular-expression-syntax) が利用可能です
- Interrogatorを使用してタグの追加や編集ができます
  - BLIP、DeepDanbooru、[Z3D-E621-Convnext](https://huggingface.co/toynya/Z3D-E621-Convnext)、 [WDv1.4 Tagger](https://huggingface.co/SmilingWolf)の各ネットワークによる学習結果（v1, v2, v3）が使用可能です
- お好みのTaggerを `userscripts/taggers` に追加できます (`scripts.tagger.Tagger`を継承したクラスでラップしてください)
  - 当該フォルダにAesthetic Scoreに基づいたTaggerをいくつか実装しています
- 画像やキャプションファイルの一括移動・削除ができます


## 使い方
1. web UI でデータセットを作成する
    - 既にリサイズ・トリミングされた画像を使用することをお勧めします
1. データセットを読み込む
    - 必要に応じてDeepDanbooru等でタグ付けができます
1. キャプションを編集する
    - "Filter by Tags" タブでキャプションの編集をしたい画像を絞り込む
    - 画像を手動で選んで絞り込む場合は "Filter by Selection" タブを使用する
    - 一括でタグを置換・削除・追加する場合は "Batch Edit Caption" タブを使用する
    - キャプションを個別に編集したい場合は "Edit Caption of Selected Image" タブを使用する
      - DeepDanbooru等も利用可能
    - 選択したものをデータセットから一括移動・削除したい場合は "Remove or Delete Files" タブを使用する
1. "Save all changes" ボタンをクリックして保存する


## タグ編集の手引き

基本的な手順は以下の通りです

1. 編集対象の画像をフィルターで絞り込む
1. まとめて編集する

一括で行われる編集はすべて**表示されている画像（＝絞り込まれた画像）にのみ**適用されます。

### 1. フィルターの選び方
- **全ての画像を一括で処理したい場合**  
  フィルターは不要です。
- **何枚かを処理したい場合**  
  1. **共通のタグや、共通して持たないタグがある**  
    "Filter by Tags" タブで画像を絞り込み、編集対象だけが表示されるようにする。
  1. **何も共通点が無い**  
    "Filter by Selection" タブで画像を絞り込む。 
    フィルターへの画像の追加は[Enter]キーがショートカットです。

### 2. 編集の仕方
- **新しいタグを追加したい場合**
  1. "Batch Edit Captions" タブを開く
  1. "Edit tags" 内に追加したいタグをカンマ区切りで追記する
  1. "Apply changes to filtered images" ボタンを押す
  ![](pic/ss08.png)  
  例："foo" と "bar" が表示されている画像に追加されます

- **絞り込まれた画像に共通なタグを編集（置換）したい場合**
  1. "Batch Edit Captions" タブを開く
  1. "Edit tags" 内に表示されたタグを書き換える
  1. "Apply changes to filtered images" ボタンを押す
  ![](pic/ss09.png)  
  例："male focus" と "solo" がそれぞれ "foo" と "bar" に置換されます

- **タグを取り除きたい場合**  
  置換と同様の手順で、対象のタグを空欄に書き換えることで取り除けます。  
  共通のタグでない（一部の画像にのみ含まれる等）場合は、"Batch Edit Captions" タブにある "Remove" を利用することもできます。

- **柔軟にタグを追加・削除・置換した**
  1. "Batch Edit Captions" タブを開く
  2. "Use regex" にチェックを入れて "Search and Replace" する  
  ![](pic/ss10.png)  
  例："1boy", "2boys", … がそれぞれ、 "1girl", "2girls", … に置換されます。  
  カンマはタグの区切りとみなされるため、カンマを追加・削除することで新しいタグを追加・削除できます。  
  正規表現（regex）を使うと、複雑な条件に応じてタグの編集が可能です。


## トラブルシューティング
### ギャラリーに画像が表示されず、コンソールに "All files must contained within the Gradio python app working directory…" と出ている
"Settings" タブで、サムネイル画像を一時保存するフォルダを指定してください。
"Directory to save temporary files" にパスを指定して "Force using temporary file…" をチェックしてください。

### 大量の画像や巨大な画像を開いたときに動作が遅くなる
"Settings" タブで、"Force image gallery to use temporary files" にチェックを入れて、 "Maximum resolution of ..." に希望の解像度を入れてください。  
数百万もの画像を含むなど、あまりにも巨大なデータセットでは効果がないかもしれません。  
もしくは、[**スタンドアロン版**](https://github.com/toshiaki1729/dataset-tag-editor-standalone)を試してください。  
![](pic/ss12.png) 


## 表示内容

[こちら](DESCRIPTION_OF_DISPLAY-JP.md)に移動しました