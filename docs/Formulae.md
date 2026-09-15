# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

# **Mathematical Formulae**

Notation: two aligned series $X_1..X_n$ and $Y_1..Y_n$ (after optional detrending), sample means
$\bar{X}, \bar{Y}$.

## 0. Pre-processing (`detrend`)

| Option | Transformation |
|---|---|
| `none` | $X_t$ (levels) |
| `linear` | $X_t - (\hat{a} + \hat{b}t)$, least-squares line removed |
| `difference` | $\Delta X_t = X_t - X_{t-1}$ (one observation fewer) |

---

## 1. Pearson Correlation Coefficient ($r$)

$$
r = \frac{\sum_{i=1}^n (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum_{i=1}^n (X_i - \bar{X})^2}\sqrt{\sum_{i=1}^n (Y_i - \bar{Y})^2}}
$$

Measures linear association.

## 2. Spearman's Rank Correlation ($\rho$)

Pearson correlation of the ranks. Without ties:

$$
\rho = 1 - \frac{6 \sum_{i=1}^n d_i^2}{n(n^2 - 1)}, \qquad d_i = \operatorname{rank}(X_i) - \operatorname{rank}(Y_i)
$$

Measures monotonic association.

## 3. Kendall's Tau-b ($\tau$)

$$
\tau = \frac{C - D}{\sqrt{(C + D + T_X)(C + D + T_Y)}}
$$

$C$ concordant pairs, $D$ discordant pairs, $T_X$ / $T_Y$ pairs tied only in $X$ / only in $Y$.

---

## 4. Significance testing

### 4.1 Effective sample size

Autocorrelated observations carry less information than independent ones. With sample
autocorrelations $\rho_{XX}(j)$ and $\rho_{YY}(j)$ (Pyper & Peterman, 1998):

$$
\frac{1}{N^*} = \frac{1}{n} + \frac{2}{n}\sum_{j=1}^{n/5} \frac{n - j}{n}\,\rho_{XX}(j)\,\rho_{YY}(j),
\qquad 3 \le N^* \le n
$$

Reported as `n_effective`. When `autocorrelation_adjustment=False`, $N^* = n$ and SciPy's p-values
are used unchanged (`*_p_raw`).

### 4.2 p-values

Pearson and Spearman (t approximation, $N^* - 2$ degrees of freedom):

$$
t = |r|\sqrt{\frac{N^* - 2}{1 - r^2}}, \qquad p = 2\,P(T_{N^*-2} > t)
$$

Kendall (normal approximation):

$$
z = \frac{3|\tau|\sqrt{N^*(N^* - 1)}}{\sqrt{2(2N^* + 1)}}, \qquad p = 2\,P(Z > z)
$$

### 4.3 Multiple testing

With `fdr_correction=True`, the p-values of each method are replaced by Benjamini-Hochberg adjusted
values (q-values) across all analysed pairs. For $m$ pairs with sorted p-values $p_{(1)} \le \dots \le p_{(m)}$:

$$
q_{(i)} = \min_{k \ge i} \min\left(1, \frac{m}{k}\,p_{(k)}\right)
$$

A method is **significant** for a pair when its final p-value (`*_p`) is below `alpha`.

---

## 5. Cross-Correlation Function (CCF)

**Sign convention:** lag $k > 0$ means $X$ **leads** $Y$ by $k$ observations.

$$
\text{CCF}(k) = \frac{\sum_{t} (X_t - \bar{X})(Y_{t+k} - \bar{Y})}{n\,s_X s_Y},
\qquad k = -K, \dots, K
$$

with population standard deviations $s_X, s_Y$, summing over the $n - |k|$ overlapping pairs.
$\text{CCF}(0) = r$. $K$ is `max_lag` (clipped to $n - 3$).

### 5.1 Pre-whitening (`prewhiten=True`)

Autocorrelation smears cross-correlation across many lags and invalidates simple bands. Each series
is filtered with its own autoregressive model, chosen by AIC up to order
$p_{max} = \min(10, n/5)$ and fitted by Yule-Walker (Levinson-Durbin):

$$
e^X_t = (X_t - \bar{X}) - \sum_{i=1}^{p_X} \hat{\phi}^X_i (X_{t-i} - \bar{X})
$$

and likewise $e^Y_t$. The CCF used for lag detection is the CCF of the residuals $e^X, e^Y$
(double pre-whitening; Haugh, 1976), which does not depend on pair order.

### 5.2 Significance band

For $L = 2K + 1$ searched lags (Bonferroni):

$$
b = \frac{z_{1 - \alpha / (2L)}}{\sqrt{n_b}}
$$

where $n_b$ is the effective sample size (4.1) of the residuals when pre-whitened, or $n$ otherwise.

### 5.3 Lead/lag detection

With $k^* = \arg\max_k |\text{CCF}(k)|$, a lead/lag is **detected** when

$$
|\text{CCF}(k^*)| > b, \qquad k^* \ne 0, \qquad L_r = \frac{|\text{CCF}(k^*)|}{|\text{CCF}(0)|} \ge \texttt{lag\_min\_ratio}
$$

Reported as `ccf_peak`, `ccf_peak_lag`, `ccf_band`, `lag_ratio` and `lag_detected`.

---

## 6. Rolling Window Correlation ($r_w$)

$$
r_w(t) = r\left(X_{[t-w+1:t]},\, Y_{[t-w+1:t]}\right)
$$

$w$ is `rolling_window`. Reported as `rolling_mean` and `rolling_std` (stability of the relationship).

---

## 7. Relationship classification

Let $S$ be the number of significant methods (of 3) and $M = \max(|r|, |\rho|, |\tau|)$.
Rules are applied in order:

| Type | Condition |
|---|---|
| `none` | ($S = 0$ or $M <$ `min_correlation`) and no lead/lag detected |
| `lagged` | lead/lag detected but ($S = 0$ or $M <$ `min_correlation`) |
| `linear` | $\lvert r - \rho \rvert <$ `linear_max_rank_gap` and $\text{sd}(r_w) <$ `linear_max_rolling_std` |
| `non_linear` | $\lvert\rho\rvert - \lvert r\rvert >$ `nonlinear_min_rank_gain` |
| `lagged` | lead/lag detected |
| `complex` | otherwise (related, but unstable or methods disagree) |

## 8. Evidence score ($E$)

$$
E = \max\left(\frac{S}{3} \cdot M,\;\; \mathbb{1}[\text{lag detected}] \cdot |\text{CCF}(k^*)|\right) \in [0, 1]
$$

The evidence score ranks pairs by strength weighted by statistical support. It is a heuristic
ranking, not a probability.

---

## 9. Limitations

- The effective sample size corrects well for stationary autocorrelated series (about 6% false
  positives at $\alpha = 0.05$ in simulation) but is less reliable for random walks and strong
  deterministic trends (about 14-15%). Use `detrend="difference"` or `"linear"` for such data; reports
  flag series with lag-1 autocorrelation of at least 0.95.
- With short series (e.g. $n = 52$), AR models and residual bands are approximate. Treat detected
  lead/lag relationships as hypotheses to confirm.
- Correlation is not causation, and a lead/lag is not Granger causality.

## References

- Pyper, B. J., & Peterman, R. M. (1998). Comparison of methods to account for autocorrelation in
  correlation analyses of fish data. *Canadian Journal of Fisheries and Aquatic Sciences*, 55(9), 2127-2140.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal
  Statistical Society B*, 57(1), 289-300.
- Haugh, L. D. (1976). Checking the independence of two covariance-stationary time series: a
  univariate residual cross-correlation approach. *Journal of the American Statistical Association*, 71(354), 378-385.
- Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). *Time Series Analysis:
  Forecasting and Control* (5th ed.). Wiley.
