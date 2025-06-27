
let isWait = false;
const PTAG_TALK_CLASS = 'talk-text';
const DIVTAG_TEXT_BIX_ID = 'user-input';
const DIVTAG_TALK_CONTAINER = 'talk-container';

document.getElementById('send-button').addEventListener('click', function() {

    const textBox = document.getElementById(DIVTAG_TEXT_BIX_ID);
    const talkContainer = document.getElementById(DIVTAG_TALK_CONTAINER);
    
    if (textBox.value.trim() !== "" && !isWait) {
        isWait = true;
        // テキストボックスをトーク履歴に追加
        const userMessage = document.createElement('div');
        userMessage.classList.add('message', 'user');
        userMessage.innerHTML = `<p class="${PTAG_TALK_CLASS}">${textBox.value}</p>`;
        textBox.value = '';
        talkContainer.appendChild(userMessage);
        // トーク履歴の取得
        const pTags = talkContainer.getElementsByTagName('p');
        const filteredPTags = Array.from(pTags).filter(pTag => pTag.classList.contains(PTAG_TALK_CLASS));
        const msg_dicts = get_msg_dicts(filteredPTags);
        // spnserの追加
        const botMessage = document.createElement('div');
        botMessage.classList.add('message', 'bot');
        botMessage.innerHTML = `<div class="spinner"></div><p>しばらくお待ちください</p>`;
        talkContainer.appendChild(botMessage);

        talkContainer.scrollTop = talkContainer.scrollHeight;

        // データの送信
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json',},
            body: JSON.stringify({'msg_dists' : msg_dicts}),
        })
        .then(response => response.json())
        .then(data => {
            botMessage.innerHTML = `<p class="${PTAG_TALK_CLASS}">${data.bot_msg}</p>`;
            talkContainer.scrollTop = talkContainer.scrollHeight;
            const productInfo = data.product_info;
            add_product_info(talkContainer, productInfo);
            isWait = false;
        })
        .catch((error) => {
            console.error('Error:', error);
            isWait = false;
        });
    }
});


function add_product_info(talkContainer, productInfo) {
    if (productInfo.length == 0){ return };
    const productContainer = document.createElement('div');
    productContainer.classList.add('product_container');
    for (let i = 0; i < productInfo.length; i++) {
        const name = productInfo[i]["name"];
        const url = productInfo[i]["url"];
        // 各商品のコンテナを生成
        const productDiv = document.createElement('div');
        productDiv.classList.add('product');
        productDiv.classList.add(`product-items${String(i).padStart(3, '0')}`);
        // 商品名を追加
        const nameParagraph = document.createElement('p');
        nameParagraph.textContent = name;
        // ボタンを追加
        const button = document.createElement('button');
        button.classList.add('buy-button');
        button.textContent = '購入';
        button.onclick = () => {window.open(url, '_blank');};
        // 商品コンテナに追加
        productDiv.appendChild(nameParagraph);
        productDiv.appendChild(button);
        // 親コンテナに追加
        productContainer.appendChild(productDiv);
    }
    // メインコンテナに追加
    talkContainer.appendChild(productContainer);
    // スクロール位置を調整
    talkContainer.scrollTop = talkContainer.scrollHeight;
}





function get_msg_dicts(pTags) {
    DEFAULT_SYSTEM_PROMPT = "\
        あなたはヒアリングが得意な医師AIです。\
        あなたは患者の気づいていない医薬品への要望を聞き出せます。\
        また、医薬品に関する知識を問う問題には答えません。\
        あなたはあくまで、ヒアリングを行うだけです。\
        注意: あなたは自然な対話を心がけます。\
        注意: 市販薬の範疇を超えている場合、必ず病院に行くことを進めてください。"

    let msg_dicts = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
    for (let i = 0; i < pTags.length; i++){
        let pTagText = pTags[i].textContent;
        if (i % 2 == 0){
            msg_dicts.push({"role": "assistant", "content": pTagText});
        }else{
            msg_dicts.push({"role": "user", "content": pTagText});
        };
    };
    return msg_dicts
};
