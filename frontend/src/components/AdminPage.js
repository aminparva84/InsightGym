import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './AdminPage.css';

const AdminPage = () => {
  const { t, i18n } = useTranslation();
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [editingExercise, setEditingExercise] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    category: 'bodybuilding_machine',
    name_fa: '',
    name_en: '',
    target_muscle_fa: '',
    target_muscle_en: '',
    level: 'beginner',
    intensity: 'light',
    breathing_guide_fa: '',
    breathing_guide_en: '',
    execution_tips_fa: '',
    execution_tips_en: '',
    gender_suitability: 'both',
    injury_contraindications: [],
    equipment_needed_fa: '',
    equipment_needed_en: ''
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    category: '',
    level: ''
  });

  useEffect(() => {
    checkAdmin();
    fetchExercises();
  }, [currentPage, filters]);

  const checkAdmin = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/admin/check-admin');
      setIsAdmin(response.data.is_admin);
      if (!response.data.is_admin) {
        alert('You are not authorized to access this page');
        window.location.href = '/dashboard';
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
      setIsAdmin(false);
    }
  };

  const fetchExercises = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        per_page: 20,
        ...filters
      };
      const response = await axios.get('http://localhost:5000/api/admin/exercises', { params });
      setExercises(response.data.exercises);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error('Error fetching exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleInjuryChange = (e) => {
    const { value, checked } = e.target;
    setFormData(prev => {
      const injuries = prev.injury_contraindications || [];
      if (checked) {
        return { ...prev, injury_contraindications: [...injuries, value] };
      } else {
        return { ...prev, injury_contraindications: injuries.filter(i => i !== value) };
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingExercise) {
        await axios.put(`http://localhost:5000/api/admin/exercises/${editingExercise.id}`, formData);
      } else {
        await axios.post('http://localhost:5000/api/admin/exercises', formData);
      }
      setEditingExercise(null);
      setShowAddForm(false);
      resetForm();
      fetchExercises();
    } catch (error) {
      console.error('Error saving exercise:', error);
      alert('Error saving exercise: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleEdit = (exercise) => {
    setEditingExercise(exercise);
    setFormData({
      category: exercise.category,
      name_fa: exercise.name_fa,
      name_en: exercise.name_en,
      target_muscle_fa: exercise.target_muscle_fa,
      target_muscle_en: exercise.target_muscle_en,
      level: exercise.level,
      intensity: exercise.intensity,
      breathing_guide_fa: exercise.breathing_guide_fa || '',
      breathing_guide_en: exercise.breathing_guide_en || '',
      execution_tips_fa: exercise.execution_tips_fa || '',
      execution_tips_en: exercise.execution_tips_en || '',
      gender_suitability: exercise.gender_suitability,
      injury_contraindications: exercise.injury_contraindications || [],
      equipment_needed_fa: exercise.equipment_needed_fa || '',
      equipment_needed_en: exercise.equipment_needed_en || ''
    });
    setShowAddForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this exercise?')) {
      return;
    }
    try {
      await axios.delete(`http://localhost:5000/api/admin/exercises/${id}`);
      fetchExercises();
    } catch (error) {
      console.error('Error deleting exercise:', error);
      alert('Error deleting exercise: ' + (error.response?.data?.error || error.message));
    }
  };

  const resetForm = () => {
    setFormData({
      category: 'bodybuilding_machine',
      name_fa: '',
      name_en: '',
      target_muscle_fa: '',
      target_muscle_en: '',
      level: 'beginner',
      intensity: 'light',
      breathing_guide_fa: '',
      breathing_guide_en: '',
      execution_tips_fa: '',
      execution_tips_en: '',
      gender_suitability: 'both',
      injury_contraindications: [],
      equipment_needed_fa: '',
      equipment_needed_en: ''
    });
  };

  const injuryOptions = ['knee', 'shoulder', 'lower_back', 'neck', 'elbow', 'wrist', 'ankle', 'hip'];

  if (!isAdmin) {
    return <div className="admin-page">Checking authorization...</div>;
  }

  return (
    <div className="admin-page">
      <div className="admin-header">
        <h1>Exercise Library Management</h1>
        <button className="btn-add" onClick={() => { setShowAddForm(true); setEditingExercise(null); resetForm(); }}>
          Add New Exercise
        </button>
      </div>

      <div className="admin-filters">
        <select 
          value={filters.category} 
          onChange={(e) => { setFilters({...filters, category: e.target.value}); setCurrentPage(1); }}
        >
          <option value="">All Categories</option>
          <option value="bodybuilding_machine">Bodybuilding Machine</option>
          <option value="functional_home">Functional Home</option>
          <option value="hybrid_hiit_machine">Hybrid/HIIT</option>
        </select>
        <select 
          value={filters.level} 
          onChange={(e) => { setFilters({...filters, level: e.target.value}); setCurrentPage(1); }}
        >
          <option value="">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      {showAddForm && (
        <div className="admin-form-overlay">
          <div className="admin-form-container">
            <h2>{editingExercise ? 'Edit Exercise' : 'Add New Exercise'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>Category *</label>
                  <select name="category" value={formData.category} onChange={handleInputChange} required>
                    <option value="bodybuilding_machine">Bodybuilding Machine</option>
                    <option value="functional_home">Functional Home</option>
                    <option value="hybrid_hiit_machine">Hybrid/HIIT</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Level *</label>
                  <select name="level" value={formData.level} onChange={handleInputChange} required>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Intensity *</label>
                  <select name="intensity" value={formData.intensity} onChange={handleInputChange} required>
                    <option value="light">Light</option>
                    <option value="medium">Medium</option>
                    <option value="heavy">Heavy</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Gender Suitability *</label>
                  <select name="gender_suitability" value={formData.gender_suitability} onChange={handleInputChange} required>
                    <option value="both">Both</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Name (Persian) *</label>
                  <input type="text" name="name_fa" value={formData.name_fa} onChange={handleInputChange} required />
                </div>
                <div className="form-group">
                  <label>Name (English) *</label>
                  <input type="text" name="name_en" value={formData.name_en} onChange={handleInputChange} required />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Target Muscle (Persian) *</label>
                  <input type="text" name="target_muscle_fa" value={formData.target_muscle_fa} onChange={handleInputChange} required />
                </div>
                <div className="form-group">
                  <label>Target Muscle (English) *</label>
                  <input type="text" name="target_muscle_en" value={formData.target_muscle_en} onChange={handleInputChange} required />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Breathing Guide (Persian)</label>
                  <textarea name="breathing_guide_fa" value={formData.breathing_guide_fa} onChange={handleInputChange} rows="3" />
                </div>
                <div className="form-group">
                  <label>Breathing Guide (English)</label>
                  <textarea name="breathing_guide_en" value={formData.breathing_guide_en} onChange={handleInputChange} rows="3" />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Execution Tips (Persian)</label>
                  <textarea name="execution_tips_fa" value={formData.execution_tips_fa} onChange={handleInputChange} rows="4" />
                </div>
                <div className="form-group">
                  <label>Execution Tips (English)</label>
                  <textarea name="execution_tips_en" value={formData.execution_tips_en} onChange={handleInputChange} rows="4" />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Equipment Needed (Persian)</label>
                  <input type="text" name="equipment_needed_fa" value={formData.equipment_needed_fa} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Equipment Needed (English)</label>
                  <input type="text" name="equipment_needed_en" value={formData.equipment_needed_en} onChange={handleInputChange} />
                </div>
              </div>

              <div className="form-group">
                <label>Injury Contraindications</label>
                <div className="injury-checkboxes">
                  {injuryOptions.map(injury => (
                    <label key={injury} className="checkbox-label">
                      <input
                        type="checkbox"
                        value={injury}
                        checked={formData.injury_contraindications.includes(injury)}
                        onChange={handleInjuryChange}
                      />
                      {injury.replace('_', ' ').toUpperCase()}
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-save">Save</button>
                <button type="button" className="btn-cancel" onClick={() => { setShowAddForm(false); setEditingExercise(null); resetForm(); }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading exercises...</div>
      ) : (
        <>
          <div className="exercises-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name (FA)</th>
                  <th>Name (EN)</th>
                  <th>Category</th>
                  <th>Level</th>
                  <th>Target Muscle</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {exercises.map(exercise => (
                  <tr key={exercise.id}>
                    <td>{exercise.id}</td>
                    <td>{exercise.name_fa}</td>
                    <td>{exercise.name_en}</td>
                    <td>{exercise.category}</td>
                    <td>{exercise.level}</td>
                    <td>{exercise.target_muscle_fa}</td>
                    <td>
                      <button className="btn-edit" onClick={() => handleEdit(exercise)}>Edit</button>
                      <button className="btn-delete" onClick={() => handleDelete(exercise.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button disabled={currentPage === 1} onClick={() => setCurrentPage(prev => prev - 1)}>
              Previous
            </button>
            <span>Page {currentPage} of {totalPages}</span>
            <button disabled={currentPage === totalPages} onClick={() => setCurrentPage(prev => prev + 1)}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default AdminPage;



