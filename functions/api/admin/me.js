import { jsonResponse } from "../../_lib/blog.js";
import { todayVancouver } from "../../_lib/blog.js";

export const onRequestGet = ({ data }) => jsonResponse({ email: data.email, today: todayVancouver() });
