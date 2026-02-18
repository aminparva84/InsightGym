import React, { useMemo, useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { getApiBase } from '../services/apiBase';
import './PurchasePage.css';

const DISCOUNT_CODE = 'FREE100';

const PurchasePage = () => {
  const { t, i18n } = useTranslation();
  const API_BASE = getApiBase();
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [purchase, setPurchase] = useState(null);
  const [discountCode, setDiscountCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    const statePayload = location.state;
    if (statePayload) {
      setPurchase(statePayload);
      try {
        localStorage.setItem('pendingPurchase', JSON.stringify(statePayload));
      } catch (err) {
        console.error('Could not save pending purchase:', err);
      }
      return;
    }
    try {
      const raw = localStorage.getItem('pendingPurchase');
      if (raw) setPurchase(JSON.parse(raw));
    } catch (err) {
      console.error('Could not read pending purchase:', err);
    }
  }, [location.state]);

  const program = useMemo(() => purchase?.program || null, [purchase]);
  const packages = useMemo(() => purchase?.packages || [], [purchase]);
  const emsForm = useMemo(() => purchase?.emsForm || null, [purchase]);

  const subtotal = useMemo(() => {
    const base = program?.price || 0;
    const pkgSum = packages.reduce((sum, p) => sum + (p.price || 0), 0);
    return base + pkgSum;
  }, [program, packages]);

  const discountAmount = useMemo(() => {
    return discountCode.trim().toUpperCase() === DISCOUNT_CODE ? subtotal : 0;
  }, [discountCode, subtotal]);

  const total = Math.max(0, subtotal - discountAmount);

  const handlePlaceOrder = async () => {
    if (!program) return;
    setIsSubmitting(true);
    setResult(null);
    try {
      const token = localStorage.getItem('token');
      const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
      const res = await axios.post(`${API_BASE}/api/member/purchase-training-program`, {
        program_id: program.id,
        base_price: program.price,
        packages,
        ems_form: emsForm,
        discount_code: discountCode.trim(),
        language: i18n.language || 'fa',
      }, config);
      setResult({ ok: true, data: res.data });
      if (res.data?.status === 'paid') {
        try {
          localStorage.removeItem('pendingPurchase');
        } catch (err) {
          console.error('Could not clear pending purchase:', err);
        }
      }
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Error';
      setResult({ ok: false, error: msg });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isPaid = result?.ok && result.data?.status === 'paid';

  if (!purchase || !program) {
    return (
      <div className="purchase-page">
        <div className="purchase-card">
          <h2>{t('purchaseTitle')}</h2>
          <p>{t('purchaseEmpty')}</p>
          <button type="button" className="program-buy-btn secondary" onClick={() => navigate(-1)}>
            {t('purchaseBack')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="purchase-page" dir={i18n.language === 'fa' ? 'rtl' : 'ltr'}>
      <div className="purchase-card">
        <div className="purchase-header">
          <h2>{t('purchaseTitle')}</h2>
          <button type="button" className="program-buy-btn secondary" onClick={() => navigate(-1)}>
            {t('purchaseBack')}
          </button>
        </div>

        <div className="purchase-section">
          <h3>{t('purchaseSummary')}</h3>
          <div className="purchase-summary-row">
            <span>{program.nameKey ? t(program.nameKey) : (i18n.language === 'fa' ? program.name_fa : program.name_en) || program.name || (i18n.language === 'fa' ? 'برنامه تمرینی' : 'Training program')}</span>
            <span>${program.price || 0}</span>
          </div>
          {packages.map((pkg) => (
            <div key={pkg.id} className="purchase-summary-row">
              <span>{pkg.nameKey ? t(pkg.nameKey) : (i18n.language === 'fa' ? pkg.name_fa : pkg.name_en) || pkg.name}</span>
              <span>+${pkg.price}</span>
            </div>
          ))}
          {emsForm && (
            <div className="purchase-summary-note">
              {t('purchaseEmsNote')}
            </div>
          )}
        </div>

        <div className="purchase-section">
          <h3>{t('purchaseDiscount')}</h3>
          <div className="purchase-discount-row">
            <input
              type="text"
              value={discountCode}
              onChange={(e) => setDiscountCode(e.target.value)}
              placeholder={t('purchaseDiscountPlaceholder')}
            />
            <div className="purchase-discount-hint">
              {t('purchaseDiscountHint', { code: DISCOUNT_CODE })}
            </div>
          </div>
        </div>

        <div className="purchase-total">
          <div className="purchase-summary-row">
            <span>{t('purchaseSubtotal')}</span>
            <span>${subtotal}</span>
          </div>
          <div className="purchase-summary-row">
            <span>{t('purchaseDiscount')}</span>
            <span>-${discountAmount}</span>
          </div>
          <div className="purchase-summary-row total">
            <span>{t('purchaseTotal')}</span>
            <span>${total}</span>
          </div>
        </div>

        {result && (
          <div className={`purchase-result ${result.ok ? 'ok' : 'err'}`}>
            {result.ok
              ? (result.data?.status === 'paid' ? t('purchaseSuccess') : t('purchasePending'))
              : t('purchaseError')}
          </div>
        )}

        {isPaid ? (
          <button
            type="button"
            className="program-buy-btn training-programs-buy-btn"
            onClick={() => navigate('/dashboard?tab=training-program')}
          >
            {t('purchaseGoToProgram')}
          </button>
        ) : (
          <button
            type="button"
            className="program-buy-btn training-programs-buy-btn"
            onClick={handlePlaceOrder}
            disabled={isSubmitting || !user}
          >
            {isSubmitting ? t('purchaseSubmitting') : t('purchasePay')}
          </button>
        )}

        {total > 0 && (
          <p className="purchase-gateway-note">{t('purchaseNoGateway')}</p>
        )}
      </div>
    </div>
  );
};

export default PurchasePage;
