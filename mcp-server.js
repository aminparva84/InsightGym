/**
 * MCP Server for Raha Fitness AI Agent
 * This server allows the AI agent to interact with the backend APIs
 */

const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const BACKEND_URL = 'http://localhost:5000/api';

/**
 * MCP Tool: Get User Exercise History
 * Allows AI to access user's exercise history
 */
async function getUserExercises(userId, token) {
  try {
    const response = await axios.get(`${BACKEND_URL}/exercises`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch exercises: ${error.message}`);
  }
}

/**
 * MCP Tool: Get User Nutrition Plans
 * Allows AI to access user's nutrition plans
 */
async function getUserNutritionPlans(userId, token, planType = '2week') {
  try {
    const response = await axios.get(`${BACKEND_URL}/nutrition/plans?type=${planType}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch nutrition plans: ${error.message}`);
  }
}

/**
 * MCP Tool: Get User Chat History
 * Allows AI to access previous conversations
 */
async function getUserChatHistory(userId, token) {
  try {
    const response = await axios.get(`${BACKEND_URL}/chat/history`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch chat history: ${error.message}`);
  }
}

/**
 * MCP Tool: Add Exercise
 * Allows AI to add exercises for the user
 */
async function addExercise(userId, token, exerciseData) {
  try {
    const response = await axios.post(`${BACKEND_URL}/exercises`, exerciseData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to add exercise: ${error.message}`);
  }
}

/**
 * MCP Tool: Add Nutrition Plan Entry
 * Allows AI to add nutrition plan entries
 */
async function addNutritionPlan(userId, token, nutritionData) {
  try {
    const response = await axios.post(`${BACKEND_URL}/nutrition/plans`, nutritionData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to add nutrition plan: ${error.message}`);
  }
}

/**
 * MCP Tool: Send Chat Message
 * Allows AI to send messages and get responses
 */
async function sendChatMessage(userId, token, message) {
  try {
    const response = await axios.post(`${BACKEND_URL}/chat`, { message }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to send chat message: ${error.message}`);
  }
}

/**
 * MCP Tool: Get Exercise Library
 * Allows AI to search and retrieve exercises from the library
 */
async function getExerciseLibrary(userId, token, params = {}) {
  try {
    const response = await axios.get(`${BACKEND_URL}/exercises/library`, {
      params,
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch exercise library: ${error.message}`);
  }
}

/**
 * MCP Tool: Search Exercises
 * Allows AI to search exercises by category, level, target muscle, or injury contraindications
 */
async function searchExercises(userId, token, searchParams) {
  try {
    const response = await axios.get(`${BACKEND_URL}/exercises/search`, {
      params: searchParams,
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to search exercises: ${error.message}`);
  }
}

/**
 * MCP Endpoint: Execute Tool
 * Main endpoint for AI agent to interact with backend
 */
app.post('/mcp/tools/execute', async (req, res) => {
  const { tool, params, userId, token } = req.body;

  try {
    let result;
    
    switch (tool) {
      case 'get_user_exercises':
        result = await getUserExercises(userId, token);
        break;
      case 'get_user_nutrition_plans':
        result = await getUserNutritionPlans(userId, token, params?.planType);
        break;
      case 'get_user_chat_history':
        result = await getUserChatHistory(userId, token);
        break;
      case 'add_exercise':
        result = await addExercise(userId, token, params);
        break;
      case 'add_nutrition_plan':
        result = await addNutritionPlan(userId, token, params);
        break;
      case 'send_chat_message':
        result = await sendChatMessage(userId, token, params?.message);
        break;
      case 'get_exercise_library':
        result = await getExerciseLibrary(userId, token, params);
        break;
      case 'search_exercises':
        result = await searchExercises(userId, token, params);
        break;
      default:
        return res.status(400).json({ error: 'Unknown tool' });
    }

    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * MCP Endpoint: List Available Tools
 */
app.get('/mcp/tools', (req, res) => {
  res.json({
    tools: [
      {
        name: 'get_user_exercises',
        description: 'Get user exercise history',
        parameters: {}
      },
      {
        name: 'get_user_nutrition_plans',
        description: 'Get user nutrition plans (2week or 4week)',
        parameters: {
          planType: { type: 'string', enum: ['2week', '4week'] }
        }
      },
      {
        name: 'get_user_chat_history',
        description: 'Get user chat history with AI assistant',
        parameters: {}
      },
      {
        name: 'add_exercise',
        description: 'Add a new exercise entry for the user',
        parameters: {
          exercise_name: { type: 'string', required: true },
          exercise_type: { type: 'string' },
          duration: { type: 'number' },
          calories_burned: { type: 'number' },
          notes: { type: 'string' }
        }
      },
      {
        name: 'add_nutrition_plan',
        description: 'Add a nutrition plan entry',
        parameters: {
          plan_type: { type: 'string', enum: ['2week', '4week'] },
          day: { type: 'number', required: true },
          meal_type: { type: 'string' },
          food_item: { type: 'string', required: true },
          calories: { type: 'number' },
          protein: { type: 'number' },
          carbs: { type: 'number' },
          fats: { type: 'number' },
          notes: { type: 'string' }
        }
      },
      {
        name: 'send_chat_message',
        description: 'Send a chat message and get AI response',
        parameters: {
          message: { type: 'string', required: true }
        }
      },
      {
        name: 'get_exercise_library',
        description: 'Get exercises from the exercise library with optional filters',
        parameters: {
          category: { type: 'string', enum: ['bodybuilding_machine', 'functional_home', 'hybrid_hiit_machine'] },
          level: { type: 'string', enum: ['beginner', 'intermediate', 'advanced'] },
          intensity: { type: 'string', enum: ['light', 'medium', 'heavy'] },
          page: { type: 'number' },
          per_page: { type: 'number' }
        }
      },
      {
        name: 'search_exercises',
        description: 'Search exercises by category, level, target muscle, or exclude exercises with specific injuries',
        parameters: {
          category: { type: 'string', enum: ['bodybuilding_machine', 'functional_home', 'hybrid_hiit_machine'] },
          level: { type: 'string', enum: ['beginner', 'intermediate', 'advanced'] },
          target_muscle: { type: 'string' },
          exclude_injuries: { type: 'array', items: { type: 'string' } },
          limit: { type: 'number' }
        }
      }
    ]
  });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`MCP Server running on port ${PORT}`);
  console.log(`Available at http://localhost:${PORT}/mcp/tools`);
});

module.exports = app;

