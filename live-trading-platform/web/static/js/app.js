let ws = null;
let priceChart = null;
let priceData = {};
let currentChartSymbol = 'BTC-USD';

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(protocol + '//' + window.location.host);
    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'price') {
                updatePriceCard(msg.data);
            } else if (msg.type === 'dashboard') {
                updateDashboard(msg.data);
            }
        } catch (e) {
            console.error('WS parse error', e);
        }
    };
    ws.onclose = () => {
        setTimeout(connectWebSocket, 3000);
    };
}

function updatePriceCard(data) {
    if (!priceData[data.symbol]) {
        priceData[data.symbol] = [];
        const container = document.getElementById('priceCards');
        const card = document.createElement('div');
        card.className = 'price-card';
        card.id = 'price-' + data.symbol;
        card.innerHTML = '<div class=\"symbol\">' + data.symbol + '</div><div class=\"price\">$0.00</div>';
        container.appendChild(card);
    }
    priceData[data.symbol].push({ time: Date.now(), price: data.price });
    if (priceData[data.symbol].length > 200) priceData[data.symbol].shift();
    const card = document.getElementById('price-' + data.symbol);
    if (card) {
        card.querySelector('.price').textContent = '$' + data.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
    if (data.symbol === currentChartSymbol && priceChart) {
        priceChart.data.labels = priceData[data.symbol].map(d => new Date(d.time).toLocaleTimeString());
        priceChart.data.datasets[0].data = priceData[data.symbol].map(d => d.price);
        priceChart.update('none');
    }
}

function updateDashboard(data) {
    if (data.positions) {
        const tbody = document.querySelector('#positionsTable tbody');
        tbody.innerHTML = data.positions.map(p => '<tr><td>' + p.symbol + '</td><td>' + p.quantity + '</td><td>' + p.average_entry_price + '</td><td>' + (p.current_price || '-') + '</td><td>' + (p.market_value || '-') + '</td><td>' + (p.unrealized_pnl || '-') + '</td></tr>').join('');
    }
    if (data.trades) {
        const tbody = document.querySelector('#tradesTable tbody');
        tbody.innerHTML = data.trades.slice(-20).reverse().map(t => '<tr><td>' + new Date(t.timestamp).toLocaleTimeString() + '</td><td>' + t.symbol + '</td><td>' + t.side + '</td><td>' + t.quantity + '</td><td>' + t.price + '</td><td>' + t.fee + '</td><td>' + t.pnl + '</td></tr>').join('');
    }
    if (data.orders) {
        const tbody = document.querySelector('#ordersTable tbody');
        tbody.innerHTML = data.orders.map(o => '<tr><td>' + o.id + '</td><td>' + o.symbol + '</td><td>' + o.side + '</td><td>' + o.quantity + '</td><td>' + o.order_type + '</td><td>' + o.status + '</td></tr>').join('');
    }
    if (data.health) {
        const container = document.getElementById('strategyHealth');
        container.innerHTML = data.health.map(h => '<div class=\"strategy-card\"><div class=\"name\">' + h.name + '</div><div class=\"metrics\"><div class=\"metric-item\"><span class=\"metric-label\">Trades</span><span class=\"metric-value\">' + (h.trades || 0) + '</span></div><div class=\"metric-item\"><span class=\"metric-label\">PnL</span><span class=\"metric-value\">$' + (h.pnl || 0).toFixed(2) + '</span></div></div></div>').join('');
    }
    if (data.improvements) {
        const tbody = document.querySelector('#improvementsTable tbody');
        tbody.innerHTML = data.improvements.slice(-10).reverse().map(i => '<tr><td>' + new Date(i.timestamp).toLocaleTimeString() + '</td><td>' + i.strategy + '</td><td>' + i.action + '</td><td>' + i.reason + '</td><td>' + i.metric + '</td></tr>').join('');
    }
    if (data.risk) {
        document.getElementById('var95').textContent = '$' + Math.abs(data.risk.var_95 || 0).toFixed(2);
        document.getElementById('var99').textContent = '$' + Math.abs(data.risk.var_99 || 0).toFixed(2);
        document.getElementById('stressLoss').textContent = '$' + Math.abs(data.risk.stress_test_loss || 0).toFixed(2);
        document.getElementById('beta').textContent = (data.risk.beta || 1).toFixed(2);
    }
    if (data.news) {
        const container = document.getElementById('newsContainer');
        container.innerHTML = data.news.slice(0, 10).map(n => '<div class=\"news-item\"><div class=\"news-title\">' + n.title + '</div><div class=\"news-meta\">' + n.symbol + ' | ' + n.source + ' | Sentiment: ' + (n.sentiment > 0 ? '+' : '') + n.sentiment.toFixed(2) + '</div></div>').join('');
    }
    if (data.options) {
        document.getElementById('optDelta').textContent = (data.options.total_delta || 0).toFixed(4);
        document.getElementById('optGamma').textContent = (data.options.total_gamma || 0).toFixed(4);
        document.getElementById('optTheta').textContent = (data.options.total_theta || 0).toFixed(4);
        document.getElementById('optVega').textContent = (data.options.total_vega || 0).toFixed(4);
        document.getElementById('optRho').textContent = (data.options.total_rho || 0).toFixed(4);
        if (data.options.positions && data.options.positions.length > 0) {
            document.getElementById('optIV').textContent = (data.options.positions[0].iv || 0).toFixed(4);
            const tbody = document.querySelector('#optionsTable tbody');
            tbody.innerHTML = data.options.positions.map(p => '<tr><td>' + p.symbol + '</td><td>' + p.type + '</td><td>' + p.strike + '</td><td>' + p.quantity + '</td><td>' + p.delta.toFixed(4) + '</td><td>' + p.gamma.toFixed(4) + '</td><td>' + p.theta.toFixed(4) + '</td><td>' + p.vega.toFixed(4) + '</td></tr>').join('');
        }
    }
    if (data.monte_carlo) {
        const mc = data.monte_carlo;
        document.getElementById('mcExpected').textContent = (mc.expected_return * 100).toFixed(2) + '%';
        document.getElementById('mcMedian').textContent = (mc.median_return * 100).toFixed(2) + '%';
        document.getElementById('mcP95').textContent = (mc.percentile_95 * 100).toFixed(2) + '%';
        document.getElementById('mcP5').textContent = (mc.percentile_5 * 100).toFixed(2) + '%';
        document.getElementById('mcMaxDD').textContent = (mc.max_drawdown_avg * 100).toFixed(2) + '%';
        document.getElementById('mcSuccess').textContent = (mc.success_probability * 100).toFixed(2) + '%';
    }
    if (data.performance) {
        const p = data.performance;
        document.getElementById('perfPnL').textContent = '$' + (p.total_return || 0).toFixed(2);
        document.getElementById('perfSharpe').textContent = (p.sharpe_ratio || 0).toFixed(2);
        document.getElementById('perfSortino').textContent = (p.sortino_ratio || 0).toFixed(2);
        document.getElementById('perfCalmar').textContent = (p.calmar_ratio || 0).toFixed(2);
        document.getElementById('perfWinRate').textContent = ((p.win_rate || 0) * 100).toFixed(2) + '%';
        document.getElementById('perfProfitFactor').textContent = (p.profit_factor || 0).toFixed(2);
        document.getElementById('perfTrades').textContent = p.total_trades || 0;
        document.getElementById('perfMaxWins').textContent = p.max_consecutive_wins || 0;
        document.getElementById('perfMaxLosses').textContent = p.max_consecutive_losses || 0;
    }
}

async function startPlatform() {
    const res = await fetch('/api/start', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({assets: ['crypto'], crypto_symbols: ['BTC-USD']}) });
    const data = await res.json();
    if (data.status === 'started') {
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('status').textContent = 'running';
        document.getElementById('status').className = 'status-badge running';
    }
}

async function stopPlatform() {
    const res = await fetch('/api/stop', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'stopped') {
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('status').textContent = 'stopped';
        document.getElementById('status').className = 'status-badge stopped';
    }
}

function switchChart(symbol) {
    currentChartSymbol = symbol;
    document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    if (!priceData[symbol]) priceData[symbol] = [];
    priceChart.data.labels = priceData[symbol].map(d => new Date(d.time).toLocaleTimeString());
    priceChart.data.datasets[0].data = priceData[symbol].map(d => d.price);
    priceChart.data.datasets[0].label = symbol;
    priceChart.update();
}

function initChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    priceChart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: currentChartSymbol, data: [], borderColor: '#00d4ff', backgroundColor: 'rgba(0, 212, 255, 0.1)', tension: 0.1, fill: true }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } }, y: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } } } }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    connectWebSocket();
    setInterval(async () => {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('status').textContent = data.running ? 'running' : 'stopped';
        document.getElementById('status').className = 'status-badge ' + (data.running ? 'running' : 'stopped');
    }, 5000);
});
