var newmemo_inputCount = 1
function addMemo() {
    var inputCount = newmemo_inputCount;
    var newMemoHTML = `
      <div>
        <label for="memo${inputCount}">メモ</label>
        <input type="text" id="memo${inputCount}" name="memo${inputCount}">
      </div>
    `;
    var memoContainer = document.getElementById('memoContainer');
    var newMemoDiv = document.createElement('div');
    newMemoDiv.innerHTML = newMemoHTML;
    memoContainer.appendChild(newMemoDiv);
  }

  var newtag_inputCount = 1
  function addTag() {
    var inputCount = newtag_inputCount;
    var newTagHTML = `
      <div>
        <label for="tag_name${inputCount}">タグ</label>
        <input type="text" id="tag_name${inputCount}" name="tag_name${inputCount}">
        <label for="tag_color${inputCount}">色</label>
        <select id="tag_color${inputCount}" name="tag_color${inputCount}">
            <option value="黒">黒</option>
            <option value="赤">赤</option>
            <option value="緑">緑</option>
            <option value="黄">黄</option>
            <option value="青">青</option>
        </select>
      </div>
    `;
    var tagContainer = document.getElementById('tagContainer');
    var newTagDiv = document.createElement('div');
    newTagDiv.innerHTML = newTagHTML;
    tagContainer.appendChild(newTagDiv);

    newtag_inputCount++;
  }