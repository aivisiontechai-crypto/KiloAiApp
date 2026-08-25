let ws = null;
let priceChart = null;
let depthChart = null;
let priceData = {};
let candleData = {};
let currentChartSymbol = 'BTC-USD';
let currentChartType = 'line';
let currentTimeframe = '1m';
let drawings = [];
let currentDrawingTool = 'none';
let drawingPoints = [];
let chartCanvas, chartCtx;

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
        card.innerHTML = '<div class="symbol">' + data.symbol + '</div><div class="price">$0.00</div>';
        container.appendChild(card);
    }
    priceData[data.symbol].push({ time: Date.now(), price: data.price });
    if (priceData[data.symbol].length > 200) priceData[data.symbol].shift();
    const card = document.getElementById('price-' + data.symbol);
    if (card) {
        card.querySelector('.price').textContent = '$' + data.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
    if (data.symbol === currentChartSymbol && priceChart) {
        if (currentChartType === 'line') {
            priceChart.data.labels = priceData[data.symbol].map(d => new Date(d.time).toLocaleTimeString());
            priceChart.data.datasets[0].data = priceData[data.symbol].map(d => d.price);
            priceChart.update('none');
        } else {
            updateCandleData(data.symbol, data.price);
            drawCandles();
        }
    }
}

function updateCandleData(symbol, price) {
    if (!candleData[symbol]) candleData[symbol] = [];
    const now = new Date();
    const lastCandle = candleData[symbol][candleData[symbol].length - 1];
    if (lastCandle && now - lastCandle.time < 60000) {
        lastCandle.close = price;
        lastCandle.high = Math.max(lastCandle.high, price);
        lastCandle.low = Math.min(lastCandle.low, price);
    } else {
        candleData[symbol].push({ time: now, open: price, high: price, low: price, close: price, volume: 0 });
        if (candleData[symbol].length > 200) candleData[symbol].shift();
    }
}

function toHeikinAshi(candles) {
    if (!candles.length) return [];
    result = [];
    for (let i = 0; i < candles.length; i++) {
        const c = candles[i];
        if (i === 0) {
            result.push({
                time: c.time,
                open: (c.open + c.close) / 2,
                high: c.high,
                low: c.low,
                close: (c.open + c.high + c.low + c.close) / 4,
                volume: c.volume,
            });
        } else {
            const prev = result[i - 1];
            result.push({
                time: c.time,
                open: (prev.open + prev.close) / 2,
                high: Math.max(c.high, (prev.open + prev.close) / 2),
                low: Math.min(c.low, (prev.open + prev.close) / 2),
                close: (c.open + c.high + c.low + c.close) / 4,
                volume: c.volume,
            });
        }
    }
    return result;
}

function drawCandles() {
    if (!chartCtx || !candleData[currentChartSymbol]) return;
    const candles = currentChartType === 'heikin-ashi' ? toHeikinAshi(candleData[currentChartSymbol]) : candleData[currentChartSymbol];
    if (!candles.length) return;
    const width = chartCanvas.width;
    const height = chartCanvas.height;
    chartCtx.clearRect(0, 0, width, height);
    chartCtx.fillStyle = '#111827';
    chartCtx.fillRect(0, 0, width, height);
    const prices = candles.flatMap(c => [c.high, c.low]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const padding = 40;
    const candleWidth = Math.max((width - padding * 2) / candles.length - 2, 1);
    const scale = (height - padding * 2) / (maxPrice - minPrice || 1);
    for (let i = 0; i < candles.length; i++) {
        const c = candles[i];
        const x = padding + i * (candleWidth + 2);
        const isGreen = c.close >= c.open;
        chartCtx.strokeStyle = isGreen ? '#00c853' : '#ff1744';
        chartCtx.fillStyle = isGreen ? '#00c853' : '#ff1744';
        const wickTop = padding + (maxPrice - c.high) * scale;
        const wickBottom = padding + (maxPrice - c.low) * scale;
        const bodyTop = padding + (maxPrice - Math.max(c.open, c.close)) * scale;
        const bodyBottom = padding + (maxPrice - Math.min(c.open, c.close)) * scale;
        chartCtx.beginPath();
        chartCtx.moveTo(x + candleWidth / 2, wickTop);
        chartCtx.lineTo(x + candleWidth / 2, wickBottom);
        chartCtx.stroke();
        const bodyHeight = Math.max(bodyBottom - bodyTop, 1);
        chartCtx.fillRect(x, bodyTop, candleWidth, bodyHeight);
    }
    drawDrawings(candles, minPrice, maxPrice, scale, padding, candleWidth);
}

function drawDrawings(candles, minPrice, maxPrice, scale, padding, candleWidth) {
    if (!chartCtx || !drawings.length) return;
    for (const drawing of drawings) {
        if (drawing.type === 'trendline' && drawing.points.length >= 2) {
            chartCtx.strokeStyle = drawing.color || '#00d4ff';
            chartCtx.lineWidth = 2;
            chartCtx.beginPath();
            const p1 = drawing.points[0];
            const p2 = drawing.points[1];
            const x1 = padding + p1.index * (candleWidth + 2) + candleWidth / 2;
            const y1 = padding + (maxPrice - p1.price) * scale;
            const x2 = padding + p2.index * (candleWidth + 2) + candleWidth / 2;
            const y2 = padding + (maxPrice - p2.price) * scale;
            chartCtx.moveTo(x1, y1);
            chartCtx.lineTo(x2, y2);
            chartCtx.stroke();
        } else if (drawing.type === 'horizontal') {
            chartCtx.strokeStyle = drawing.color || '#00d4ff';
            chartCtx.lineWidth = 1;
            chartCtx.setLineDash([5, 5]);
            const y = padding + (maxPrice - drawing.price) * scale;
            chartCtx.beginPath();
            chartCtx.moveTo(padding, y);
            chartCtx.lineTo(chartCanvas.width - padding, y);
            chartCtx.stroke();
            chartCtx.setLineDash([]);
        } else if (drawing.type === 'fibonacci' && drawing.points.length >= 2) {
            chartCtx.strokeStyle = drawing.color || '#00d4ff';
            chartCtx.lineWidth = 1;
            const p1 = drawing.points[0];
            const p2 = drawing.points[1];
            const x1 = padding + p1.index * (candleWidth + 2) + candleWidth / 2;
            const x2 = padding + p2.index * (candleWidth + 2) + candleWidth / 2;
            const y1 = padding + (maxPrice - p1.price) * scale;
            const y2 = padding + (maxPrice - p2.price) * scale;
            const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
            chartCtx.font = '10px monospace';
            chartCtx.fillStyle = drawing.color || '#00d4ff';
            for (const level of levels) {
                const y = y1 + (y2 - y1) * level;
                chartCtx.beginPath();
                chartCtx.moveTo(x1, y);
                chartCtx.lineTo(x2, y);
                chartCtx.stroke();
                chartCtx.fillText((level * 100).toFixed(1) + '%', x2 + 5, y + 3);
            }
        }
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
        container.innerHTML = data.health.map(h => '<div class="strategy-card"><div class="name">' + h.name + '</div><div class="metrics"><div class="metric-item"><span class="metric-label">Trades</span><span class="metric-value">' + (h.trades || 0) + '</span></div><div class="metric-item"><span class="metric-label">PnL</span><span class="metric-value">$' + (h.pnl || 0).toFixed(2) + '</span></div></div></div>').join('');
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
        container.innerHTML = data.news.slice(0, 10).map(n => '<div class="news-item"><div class="news-title">' + n.title + '</div><div class="news-meta">' + n.symbol + ' | ' + n.source + ' | Sentiment: ' + (n.sentiment > 0 ? '+' : '') + n.sentiment.toFixed(2) + '</div></div>').join('');
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
    if (data.margin) {
        const margin = data.margin.crypto || data.margin.us_equity || {};
        document.getElementById('marginBuyingPower').textContent = '$' + (margin.buying_power || 0).toFixed(2);
        document.getElementById('marginUsed').textContent = '$' + (margin.margin_used || 0).toFixed(2);
        document.getElementById('marginLeverage').textContent = (margin.leverage || 1).toFixed(2) + 'x';
        document.getElementById('marginCall').textContent = margin.margin_call ? 'YES' : 'No';
        document.getElementById('marginCall').style.color = margin.margin_call ? '#ff1744' : '#e0e0e0';
    }
    if (data.journal) {
        const tbody = document.querySelector('#journalTable tbody');
        tbody.innerHTML = data.journal.slice(-20).reverse().map(j => '<tr><td>' + new Date(j.timestamp).toLocaleTimeString() + '</td><td>' + j.symbol + '</td><td>' + j.side + '</td><td>' + j.quantity + '</td><td>' + j.price + '</td><td>' + (j.pnl || 0).toFixed(2) + '</td><td>' + (j.strategy || '-') + '</td><td>' + (j.notes || '-') + '</td></tr>').join('');
    }
    if (data.time_sales) {
        const tbody = document.querySelector('#timeSalesTable tbody');
        tbody.innerHTML = data.time_sales.slice(-20).reverse().map(t => '<tr><td>' + new Date(t.timestamp).toLocaleTimeString() + '</td><td>' + t.symbol + '</td><td>' + t.price + '</td><td>' + t.quantity + '</td><td>' + t.side + '</td></tr>').join('');
        const table = document.getElementById('timeSalesTable');
        if (table) table.scrollTop = table.scrollHeight;
    }
    if (data.statement) {
        document.getElementById('stmtTotal').textContent = '$' + (data.statement.total_value || 0).toFixed(2);
        document.getElementById('stmtCash').textContent = '$' + (data.statement.cash || 0).toFixed(2);
        document.getElementById('stmtFees').textContent = '$' + (data.statement.total_fees || 0).toFixed(2);
        document.getElementById('stmtTrades').textContent = data.statement.trade_count || 0;
    }
    if (data.calendar) {
        const container = document.getElementById('calendarContainer');
        container.innerHTML = data.calendar.map(e => '<div class="calendar-event impact-' + e.impact + '"><div class="event-title">' + e.title + '</div><div class="event-meta">' + e.currency + ' | ' + new Date(e.event_time).toLocaleTimeString() + ' | Forecast: ' + (e.forecast || '-') + '</div></div>').join('');
    }
    if (data.depth) {
        updateDepthChart(data.depth);
    }
    if (data.patterns) {
        const container = document.getElementById('patternResults');
        if (container) {
            if (data.patterns.length === 0) {
                container.innerHTML = '<div class="scan-result-card"><div class="symbol">No patterns detected</div></div>';
            } else {
                container.innerHTML = data.patterns.map(p => '<div class="scan-result-card"><div class="symbol">' + p.pattern_type.replace(/_/g, ' ') + '</div><div class="signal">Confidence: ' + (p.confidence * 100).toFixed(1) + '%</div></div>').join('');
            }
        }
    }
}

function updateDepthChart(depthData) {
    if (!depthChart || !depthData.bids || !depthData.asks) return;
    const bids = depthData.bids.slice(0, 10);
    const asks = depthData.asks.slice(0, 10);
    const labels = [...bids.map(b => b.price.toFixed(2)), ...asks.map(a => a.price.toFixed(2))];
    const bidData = bids.map(b => b.quantity);
    const askData = asks.map(a => a.quantity);
    depthChart.data.labels = labels;
    depthChart.data.datasets[0].data = bidData;
    depthChart.data.datasets[1].data = askData;
    depthChart.update('none');
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
    if (!candleData[symbol]) candleData[symbol] = [];
    if (currentChartType === 'line') {
        priceChart.data.labels = priceData[symbol].map(d => new Date(d.time).toLocaleTimeString());
        priceChart.data.datasets[0].data = priceData[symbol].map(d => d.price);
        priceChart.data.datasets[0].label = symbol;
        priceChart.update();
    } else {
        drawCandles();
    }
}

function changeChartType() {
    currentChartType = document.getElementById('chartType').value;
    if (currentChartType === 'line') {
        if (priceChart) {
            priceChart.config.type = 'line';
            priceChart.data.labels = priceData[currentChartSymbol].map(d => new Date(d.time).toLocaleTimeString());
            priceChart.data.datasets[0].data = priceData[currentChartSymbol].map(d => d.price);
            priceChart.update();
        }
    } else {
        if (priceChart) {
            priceChart.config.type = 'line';
            priceChart.update('none');
        }
        drawCandles();
    }
}

function changeTimeframe() {
    currentTimeframe = document.getElementById('chartTimeframe').value;
}

function changeDrawingTool() {
    currentDrawingTool = document.getElementById('drawingTool').value;
    drawingPoints = [];
}

function initChart() {
    chartCanvas = document.getElementById('priceChart');
    chartCtx = chartCanvas.getContext('2d');
    chartCanvas.width = chartCanvas.parentElement.clientWidth;
    chartCanvas.height = 400;
    priceChart = new Chart(chartCanvas, {
        type: 'line',
        data: { labels: [], datasets: [{ label: currentChartSymbol, data: [], borderColor: '#00d4ff', backgroundColor: 'rgba(0, 212, 255, 0.1)', tension: 0.1, fill: true }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } }, y: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } } } }
    });
    chartCanvas.addEventListener('click', onChartClick);
    chartCanvas.addEventListener('mousemove', onChartMouseMove);
}

function onChartClick(e) {
    if (currentDrawingTool === 'none') return;
    const rect = chartCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const padding = 40;
    const candleWidth = Math.max((chartCanvas.width - padding * 2) / (candleData[currentChartSymbol]?.length || 1) - 2, 1);
    const index = Math.floor((x - padding) / (candleWidth + 2));
    const candles = currentChartType === 'heikin-ashi' ? toHeikinAshi(candleData[currentChartSymbol] || []) : (candleData[currentChartSymbol] || []);
    if (index < 0 || index >= candles.length) return;
    const price = getPriceFromY(y, candles);
    drawingPoints.push({ index, price, x, y });
    if (currentDrawingTool === 'trendline' && drawingPoints.length >= 2) {
        saveDrawing('trendline', drawingPoints.slice(-2));
        drawingPoints = [];
    } else if (currentDrawingTool === 'fibonacci' && drawingPoints.length >= 2) {
        saveDrawing('fibonacci', drawingPoints.slice(-2));
        drawingPoints = [];
    } else if (currentDrawingTool === 'horizontal') {
        saveDrawing('horizontal', [{ price }]);
        drawingPoints = [];
    }
}

function onChartMouseMove(e) {
    if (currentDrawingTool === 'none' || drawingPoints.length === 0) return;
    const rect = chartCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    drawCandles();
    const ctx = chartCtx;
    ctx.strokeStyle = '#00d4ff';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(drawingPoints[0].x, drawingPoints[0].y);
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.setLineDash([]);
}

function getPriceFromY(y, candles) {
    const padding = 40;
    const height = chartCanvas.height;
    const prices = candles.flatMap(c => [c.high, c.low]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const scale = (height - padding * 2) / (maxPrice - minPrice || 1);
    return maxPrice - (y - padding) / scale;
}

async function saveDrawing(type, points) {
    const res = await fetch('/api/drawings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ tool_type: type, symbol: currentChartSymbol, points, color: '#00d4ff' })
    });
    const data = await res.json();
    if (data.id) {
        drawings.push({ id: data.id, type, points, color: '#00d4ff' });
        drawCandles();
    }
}

function initDepthChart() {
    const ctx = document.getElementById('depthChart').getContext('2d');
    window.depthChart = new Chart(ctx, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Bids', data: [], backgroundColor: 'rgba(0, 200, 83, 0.7)' }, { label: 'Asks', data: [], backgroundColor: 'rgba(255, 23, 68, 0.7)' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, labels: { color: '#9ca3af' } } }, scales: { x: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } }, y: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } } } }
    });
}

async function registerWebhook() {
    const url = document.getElementById('webhookUrl').value;
    const events = document.getElementById('webhookEvents').value.split(',').map(s => s.trim());
    const res = await fetch('/api/webhooks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url, events})
    });
    const data = await res.json();
    alert('Webhook registered: ' + data.id);
    loadWebhooks();
}

async function loadWebhooks() {
    const res = await fetch('/api/webhooks');
    const data = await res.json();
    const container = document.getElementById('webhookList');
    container.innerHTML = data.map(w => '<div class="webhook-item"><span>' + w.url + '</span><span>' + w.events.join(', ') + '</span><span>' + (w.active ? 'Active' : 'Inactive') + '</span></div>').join('');
}

async function loadAccounts() {
    const res = await fetch('/api/accounts');
    const data = await res.json();
    const select = document.getElementById('accountSelect');
    select.innerHTML = data.accounts.map(a => '<option value="' + a.name + '"' + (a.name === data.current ? ' selected' : '') + '>' + a.name + ' ($' + a.balance.toLocaleString() + ')</option>').join('');
    const list = document.getElementById('accountList');
    list.innerHTML = data.accounts.map(a => '<div class="account-card"><div class="account-name">' + a.name + '</div><div class="account-balance">$' + a.balance.toLocaleString() + ' ' + a.currency + '</div></div>').join('');
}

async function switchAccount() {
    const name = document.getElementById('accountSelect').value;
    await fetch('/api/accounts/' + name + '/switch', { method: 'POST' });
    loadAccounts();
}

async function createAccount() {
    const name = prompt('Account name:');
    if (!name) return;
    const balance = parseFloat(prompt('Initial balance:', '50000'));
    await fetch('/api/accounts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ id: name.toLowerCase().replace(/\s+/g, '_'), name, balance })
    });
    loadAccounts();
}

async function loadOptionsChain() {
    const symbol = currentChartSymbol;
    const res = await fetch('/api/options/chain?symbol=' + symbol);
    const data = await res.json();
    const tbody = document.querySelector('#optionsChainTable tbody');
    tbody.innerHTML = data.map(o => '<tr><td>' + o.symbol + '</td><td>' + o.type + '</td><td>' + o.strike + '</td><td>' + o.premium.toFixed(2) + '</td><td>' + o.delta.toFixed(4) + '</td><td>' + o.gamma.toFixed(4) + '</td><td>' + o.theta.toFixed(4) + '</td><td>' + o.vega.toFixed(4) + '</td></tr>').join('');
}

async function loadPatterns() {
    const res = await fetch('/api/patterns?symbol=' + currentChartSymbol);
    const data = await res.json();
    const container = document.getElementById('patternResults');
    if (container) {
        if (data.length === 0) {
            container.innerHTML = '<div class="scan-result-card"><div class="symbol">Scanning...</div></div>';
        } else {
            container.innerHTML = data.map(p => '<div class="scan-result-card"><div class="symbol">' + p.pattern_type.replace(/_/g, ' ') + '</div><div class="signal">Confidence: ' + (p.confidence * 100).toFixed(1) + '%</div></div>').join('');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    initDepthChart();
    connectWebSocket();
    loadWebhooks();
    loadAccounts();
    loadOptionsChain();
    loadPatterns();
    setInterval(loadAccounts, 30000);
    setInterval(loadOptionsChain, 30000);
    setInterval(loadPatterns, 60000);
    setInterval(async () => {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('status').textContent = data.running ? 'running' : 'stopped';
        document.getElementById('status').className = 'status-badge ' + (data.running ? 'running' : 'stopped');
    }, 5000);
});

async function exportCSV() {
    window.open('/api/export/trades.csv', '_blank');
}

async function showTaxReport() {
    const res = await fetch('/api/reports/tax');
    const data = await res.json();
    alert('Tax Report: Gains=$' + data.total_gains.toFixed(2) + ', Losses=$' + data.total_losses.toFixed(2) + ', Net=$' + data.net_pnl.toFixed(2));
}

async function runScanner() {
    const indicator = document.getElementById('scanIndicator').value;
    const condition = document.getElementById('scanCondition').value;
    const threshold = parseFloat(document.getElementById('scanThreshold').value);
    const res = await fetch('/api/scanner/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({criteria: [{indicator, condition, threshold}]})
    });
    const data = await res.json();
    const container = document.getElementById('scanResults');
    if (data.length === 0) {
        container.innerHTML = '<div class="scan-result-card"><div class="symbol">No results</div></div>';
    } else {
        container.innerHTML = data.map(r => '<div class="scan-result-card"><div class="symbol">' + r.symbol + '</div><div class="signal">' + r.signal + '</div><div class="confidence">Confidence: ' + (r.confidence * 100).toFixed(1) + '%</div></div>').join('');
    }
}

async function submitQuickTrade() {
    const symbol = document.getElementById('tradeSymbol').value;
    const side = document.getElementById('tradeSide').value;
    const qty = parseFloat(document.getElementById('tradeQty').value);
    const type = document.getElementById('tradeType').value;
    const price = document.getElementById('tradePrice').value;
    const body = { symbol, side, quantity: qty, order_type: type };
    if (price) body.limit_price = parseFloat(price);
    const res = await fetch('/api/orders', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    });
    const data = await res.json();
    alert('Order submitted: ' + (data.order_id || 'error'));
}

async function submitBracketOrder() {
    const symbol = document.getElementById('tradeSymbol').value;
    const side = document.getElementById('tradeSide').value;
    const qty = parseFloat(document.getElementById('tradeQty').value);
    const entry = document.getElementById('tradePrice').value;
    const tp = prompt('Take Profit price:');
    const sl = prompt('Stop Loss price:');
    const res = await fetch('/api/orders/bracket', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol, side, quantity: qty, entry_price: entry ? parseFloat(entry) : undefined, take_profit: tp ? parseFloat(tp) : undefined, stop_loss: sl ? parseFloat(sl) : undefined })
    });
    const data = await res.json();
    alert('Bracket order submitted: ' + (data.order_id || 'error'));
}

async function submitOCOOrder() {
    const symbol = document.getElementById('tradeSymbol').value;
    const side = document.getElementById('tradeSide').value;
    const qty = parseFloat(document.getElementById('tradeQty').value);
    const res = await fetch('/api/orders/oco', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol, side, quantity: qty, limit_order: { limit_price: parseFloat(document.getElementById('tradePrice').value) || 0 } })
    });
    const data = await res.json();
    alert('OCO order submitted: ' + (data.order_id || 'error'));
}

async function showDailyPnl() {
    const res = await fetch('/api/reports/pnl');
    const data = await res.json();
    alert('Daily PnL: Net=$' + (data.net_pnl || 0).toFixed(2) + ', Trades=' + (data.trade_count || 0));
}

document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    switch (e.key.toLowerCase()) {
        case 'b':
            document.getElementById('tradeSide').value = 'buy';
            break;
        case 's':
            document.getElementById('tradeSide').value = 'sell';
            break;
        case 'enter':
            submitQuickTrade();
            break;
        case 'c':
            changeChartType();
            break;
        case 'd':
            const toolSelect = document.getElementById('drawingTool');
            const next = (toolSelect.selectedIndex + 1) % toolSelect.options.length;
            toolSelect.selectedIndex = next;
            changeDrawingTool();
            break;
    }
});
