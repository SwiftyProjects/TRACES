# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

# **Core Analytical Formulae**

## 1. _**Pearson Correlation Coefficient**_ ($r$)

$$
r = \frac{\sum_{i=1}^n \left(X_i - \bar{X}\right)\left(Y_i - \bar{Y}\right)}{\sqrt{\sum_{i=1}^n \left(X_i - \bar{X}\right)^2} \sqrt{\sum_{i=1}^n \left(Y_i - \bar{Y}\right)^2}}
$$

_Where:_
- $X_i$ and $Y_i$ are individual sample points
- $\bar{X}$ and $\bar{Y}$ are the means of the $X$ and $Y$ samples
- $n$ is the number of paired samples

## 2. _**Spearman's Rank Correlation Coefficient**_ ($\rho$)

$$
\rho = 1 - \frac{6 \sum_{i=1}^n d_i^2}{n\left(n^2 - 1\right)}
$$

_Where:_
- $d_i = \operatorname{rank}(X_i) - \operatorname{rank}(Y_i)$ is the difference between ranks
- $n$ is the number of observations

## 3. _**Kendall's Tau**_ ($\tau$)

$$
\tau = \frac{C - D}{\sqrt{(C + D + X)(C + D + Y)}}
$$

_Where:_
- $C$ is the number of concordant pairs
- $D$ is the number of discordant pairs
- $X$ is the number of pairs tied only in $X$
- $Y$ is the number of pairs tied only in $Y$

## 4. _**Cross-Correlation Function**_ (CCF)

$$
\text{CCF}(k) = \frac{\sum_{i=1}^{n - k} \left(X_i - \bar{X}\right)\left(Y_{i + k} - \bar{Y}\right)}{\sqrt{\sum_{i=1}^n \left(X_i - \bar{X}\right)^2} \sqrt{\sum_{i=1}^n \left(Y_i - \bar{Y}\right)^2}}
$$

_Where:_
- $k$ is the lag (shift between series)
- $n$ is the series length
- $\text{CCF}(k)$ is cross-correlation at lag $k$

## 5. _**Rolling Window Correlation**_ ($r_w$)

$$
r_w(t) = r\left(X_{[t-w+1:t]}, Y_{[t-w+1:t]}\right)
$$

_Where:_
- $w$ is the window size
- $t$ is the current time point
- $[t-w+1:t]$ represents the window interval

## 6. _**Relationship Confidence Score**_ ($C_s$)

$$
C_s = \frac{S_c}{3} \cdot \max(|r|, |\rho|, |\tau|)
$$

_Where:_
- $S_c$ is the count of significant correlations
- $r$, $\rho$, $\tau$ are Pearson, Spearman, and Kendall coefficients

## 7. _**Lag Impact Ratio**_ ($L_r$)

$$
L_r = \left|\frac{\max_{k}(\text{CCF}(k))}{\text{CCF}(0)}\right|
$$

_Where:_
- $\text{CCF}(k)$ is cross-correlation at lag $k$
- $\text{CCF}(0)$ is zero-lag correlation