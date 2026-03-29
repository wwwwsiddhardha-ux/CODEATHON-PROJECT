/**
 * API client for the Skill Investment Portfolio Engine backend.
 * All calls go through the React proxy → FastAPI on :8000
 */
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

/** Submit user profile and get full recommendations */
export const getRecommendations = (profile) =>
  api.post("/recommendations/", profile).then((r) => r.data);

/** Get weekly learning roadmap */
export const getRoadmap = (profile) =>
  api.post("/roadmap/", profile).then((r) => r.data);

/** Fetch real-time market demand for a list of skills */
export const getMarketDemand = (skills) =>
  api.post("/market/demand", { skills }).then((r) => r.data);

/** Save user profile */
export const saveProfile = (profile) =>
  api.post("/profile/", profile).then((r) => r.data);
