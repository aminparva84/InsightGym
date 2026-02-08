import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './TrainingPlansProductsTab.css';

const API_BASE = getApiBase();

const DEFAULT_BASE = [
  { id: 1, name_fa: 'برنامه مبتدی', name_en: 'Beginner Program', description_fa: 'مناسب برای تازه‌کارها', description_en: 'Perfect for beginners', price: 99, features: [{ key: 'feature1', text_fa: 'برنامه تمرینی هفتگی', text_en: 'Weekly workout plan' }, { key: 'feature2', text_fa: 'راهنمایی تغذیه', text_en: 'Nutrition guidance' }, { key: 'feature3', text_fa: 'پشتیبانی آنلاین', text_en: 'Online support' }] },
  { id: 2, name_fa: 'برنامه متوسط', name_en: 'Intermediate Program', description_fa: 'برای افرادی که آماده چالش بیشتر هستند', description_en: 'For those ready for more challenges', price: 149, features: [{ key: 'feature1', text_fa: 'برنامه تمرینی هفتگی', text_en: 'Weekly workout plan' }, { key: 'feature2', text_fa: 'راهنمایی تغذیه', text_en: 'Nutrition guidance' }, { key: 'feature3', text_fa: 'پشتیبانی آنلاین', text_en: 'Online support' }, { key: 'feature4', text_fa: 'بررسی پیشرفت', text_en: 'Progress tracking' }] },
  { id: 3, name_fa: 'برنامه پیشرفته', name_en: 'Advanced Program', description_fa: 'برنامه جامع برای رسیدن به اهداف تناسب اندام', description_en: 'Comprehensive program to achieve your fitness goals', price: 199, features: [{ key: 'feature1', text_fa: 'برنامه تمرینی هفتگی', text_en: 'Weekly workout plan' }, { key: 'feature2', text_fa: 'راهنمایی تغذیه', text_en: 'Nutrition guidance' }, { key: 'feature3', text_fa: 'پشتیبانی آنلاین', text_en: 'Online support' }, { key: 'feature4', text_fa: 'بررسی پیشرفت', text_en: 'Progress tracking' }, { key: 'feature5', text_fa: 'مشاوره شخصی', text_en: 'Personal coaching' }] }
];

const DEFAULT_PACKAGES = [
  { id: 'vip', name_fa: 'بسته VIP', name_en: 'VIP Package', price: 80 },
  { id: 'weeklyPlan', name_fa: 'برنامه تمرینی هفتگی', name_en: 'Weekly workout plan', price: 25 },
  { id: 'nutrition', name_fa: 'راهنمایی تغذیه', name_en: 'Nutrition guidance', price: 30 },
  { id: 'onlineSupport', name_fa: 'پشتیبانی آنلاین', name_en: 'Online support', price: 25 },
  { id: 'progressTracking', name_fa: 'بررسی پیشرفت', name_en: 'Progress tracking', price: 20 },
  { id: 'personalCoaching', name_fa: 'مشاوره شخصی', name_en: 'Personal coaching', price: 50 },
  { id: 'lifetimeAccess', name_fa: 'دسترسی مادام‌العمر', name_en: 'Lifetime access', price: 100 },
  { id: 'assessment', name_fa: 'ارزیابی اولیه شخصی', name_en: 'Personal assessment', price: 40 },
  { id: 'months3', name_fa: 'برنامه ۳ ماهه', name_en: '3-month program', price: 60 }
];

const TrainingPlansProductsTab = () => {
  const { i18n } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [basePrograms, setBasePrograms] = useState(DEFAULT_BASE);
  const [packages, setPackages] = useState(DEFAULT_PACKAGES);

  const getAuthToken = useCallback(() => localStorage.getItem('token') || '', []);
  const getAxiosConfig = useCallback(() => ({
    headers: { Authorization: `Bearer ${getAuthToken()}`, 'Content-Type': 'application/json' }
  }), [getAuthToken]);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE}/api/admin/training-plans-products`, getAxiosConfig());
      const d = res.data || {};
      if (Array.isArray(d.basePrograms) && d.basePrograms.length > 0) setBasePrograms(d.basePrograms);
      if (Array.isArray(d.packages) && d.packages.length > 0) setPackages(d.packages);
    } catch (err) {
      console.error('Error loading training plans/products:', err);
    } finally {
      setLoading(false);
    }
  }, [getAxiosConfig]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSave = async () => {
    try {
      setSaving(true);
      await axios.put(`${API_BASE}/api/admin/training-plans-products`, { basePrograms, packages }, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'ذخیره شد' : 'Saved');
    } catch (err) {
      console.error('Error saving:', err);
      alert(i18n.language === 'fa' ? 'خطا در ذخیره' : 'Error saving');
    } finally {
      setSaving(false);
    }
  };

  const updateProgram = (index, field, value) => {
    setBasePrograms(prev => {
      const next = [...prev];
      next[index] = { ...(next[index] || {}), [field]: value };
      return next;
    });
  };

  const updateProgramFeature = (programIndex, featureIndex, field, value) => {
    setBasePrograms(prev => {
      const next = [...prev];
      const prog = next[programIndex];
      if (!prog || !Array.isArray(prog.features)) return prev;
      const feats = [...prog.features];
      feats[featureIndex] = { ...(feats[featureIndex] || {}), [field]: value };
      next[programIndex] = { ...prog, features: feats };
      return next;
    });
  };

  const updatePackage = (index, field, value) => {
    setPackages(prev => {
      const next = [...prev];
      next[index] = { ...(next[index] || {}), [field]: value };
      return next;
    });
  };

  if (loading) {
    return <div className="tpp-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
  }

  const fa = i18n.language === 'fa';
  return (
    <div className="training-plans-products-tab" dir="ltr">
      <div className="tpp-header">
        <h2>{fa ? 'برنامه‌ها و بسته‌های خرید' : 'Training Plans & Packages'}</h2>
        <p className="tpp-desc">{fa ? 'زیرنویس و توضیحات برنامه‌های پایه و بسته‌ها را ویرایش کنید.' : 'Edit sub-info (names, descriptions) of base programs and packages shown in the buy modal.'}</p>
        <button type="button" className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? (fa ? 'در حال ذخیره...' : 'Saving...') : (fa ? 'ذخیره' : 'Save')}
        </button>
      </div>
      <section className="tpp-section">
        <h3>{fa ? 'برنامه‌های پایه' : 'Base programs'}</h3>
        {basePrograms.map((prog, idx) => (
          <div key={prog.id || idx} className="tpp-card">
            <h4>{fa ? 'برنامه' : 'Program'} {prog.id}</h4>
            <div className="tpp-row">
              <div className="form-group">
                <label>{fa ? 'نام (فارسی)' : 'Name (FA)'}</label>
                <input value={prog.name_fa || ''} onChange={(e) => updateProgram(idx, 'name_fa', e.target.value)} />
              </div>
              <div className="form-group">
                <label>{fa ? 'نام (انگلیسی)' : 'Name (EN)'}</label>
                <input value={prog.name_en || ''} onChange={(e) => updateProgram(idx, 'name_en', e.target.value)} />
              </div>
            </div>
            <div className="tpp-row">
              <div className="form-group">
                <label>{fa ? 'توضیح (فارسی)' : 'Description (FA)'}</label>
                <input value={prog.description_fa || ''} onChange={(e) => updateProgram(idx, 'description_fa', e.target.value)} />
              </div>
              <div className="form-group">
                <label>{fa ? 'توضیح (انگلیسی)' : 'Description (EN)'}</label>
                <input value={prog.description_en || ''} onChange={(e) => updateProgram(idx, 'description_en', e.target.value)} />
              </div>
            </div>
            <div className="form-group tpp-price">
              <label>{fa ? 'قیمت ($)' : 'Price ($)'}</label>
              <input type="number" min={0} value={prog.price ?? ''} onChange={(e) => updateProgram(idx, 'price', parseInt(e.target.value, 10) || 0)} />
            </div>
            <div className="tpp-features">
              <label>{fa ? 'ویژگی‌ها' : 'Features'}</label>
              {(prog.features || []).map((f, fi) => (
                <div key={fi} className="tpp-feature-row">
                  <input placeholder={fa ? 'متن (فا)' : 'Text (FA)'} value={f.text_fa || ''} onChange={(e) => updateProgramFeature(idx, fi, 'text_fa', e.target.value)} />
                  <input placeholder={fa ? 'متن (EN)' : 'Text (EN)'} value={f.text_en || ''} onChange={(e) => updateProgramFeature(idx, fi, 'text_en', e.target.value)} />
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>
      <section className="tpp-section">
        <h3>{fa ? 'بسته‌ها' : 'Packages'}</h3>
        {packages.map((pkg, idx) => (
          <div key={pkg.id || idx} className="tpp-card tpp-package">
            <div className="tpp-row">
              <div className="form-group">
                <label>{pkg.id} – {fa ? 'نام (فا)' : 'Name (FA)'}</label>
                <input value={pkg.name_fa || ''} onChange={(e) => updatePackage(idx, 'name_fa', e.target.value)} />
              </div>
              <div className="form-group">
                <label>{fa ? 'نام (EN)' : 'Name (EN)'}</label>
                <input value={pkg.name_en || ''} onChange={(e) => updatePackage(idx, 'name_en', e.target.value)} />
              </div>
              <div className="form-group tpp-price">
                <label>{fa ? 'قیمت ($)' : 'Price ($)'}</label>
                <input type="number" min={0} value={pkg.price ?? ''} onChange={(e) => updatePackage(idx, 'price', parseInt(e.target.value, 10) || 0)} />
              </div>
            </div>
          </div>
        ))}
      </section>
      <div className="tpp-actions">
        <button type="button" className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? (fa ? 'در حال ذخیره...' : 'Saving...') : (fa ? 'ذخیره' : 'Save')}
        </button>
      </div>
    </div>
  );
};

export default TrainingPlansProductsTab;
