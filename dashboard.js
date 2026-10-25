const form = document.getElementById('product-form');
const container = document.getElementById('products-container');
form.addEventListener('submit', function(e) {
  e.preventDefault();
  const name = document.getElementById('prod-name').value;
  const price = document.getElementById('prod-price').value;
  const item = document.createElement('div');
  item.className = 'product-item';
  item.innerHTML = `
    <div class="product-placeholder-img">📦</div>
    <div class="product-details">
      <h4>${name}</h4>
      <p>$${parseFloat(price).toFixed(2)}</p>
    </div>
  `;
  container.insertBefore(item, container.firstChild);
  form.reset();
});