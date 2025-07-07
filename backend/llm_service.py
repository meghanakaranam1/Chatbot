import re
import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from backend.crud import execute_sql_query, get_database_schema

# Try to import ML libraries, but continue without them if not available
try:
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False
    print("ML libraries not available - using intelligent flexible SQL generation")

class LLMService:
    def __init__(self):
        self.sql_generator = None
        
        if HAS_ML_LIBS:
            try:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"Using device: {self.device}")
                
                # Initialize a lighter model for SQL generation
                # Using CodeT5 which is good for code generation tasks
                self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
                self.model = AutoModelForCausalLM.from_pretrained("Salesforce/codet5-base")
                self.sql_generator = pipeline(
                    "text2text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device == "cuda" else -1
                )
                print("LLM model loaded successfully!")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.sql_generator = None
        else:
            print("Using rule-based SQL generation (no ML libraries available)")
    
    def extract_intent(self, query: str) -> Dict[str, Any]:
        """Extract intent and entities from natural language query"""
        query_lower = query.lower()
        
        intent_patterns = {
            "select": ["show", "get", "find", "list", "display", "what", "which", "how many"],
            "count": ["count", "how many", "number of"],
            "filter": ["where", "with", "having", "filter"],
            "aggregate": ["total", "sum", "average", "avg", "max", "min", "maximum", "minimum"],
            "join": ["user", "customer", "order", "product", "bought", "purchased"]
        }
        
        entities = {
            "tables": [],
            "columns": [],
            "conditions": [],
            "aggregations": []
        }
        
        # Detect table references
        table_keywords = {
            "users": ["user", "customer", "people", "person"],
            "products": ["product", "item", "goods"],
            "orders": ["order", "purchase", "transaction"],
            "order_items": ["order item", "purchased item"]
        }
        
        for table, keywords in table_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                entities["tables"].append(table)
        
        # Detect intent
        intent = "select"  # default
        for intent_type, keywords in intent_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                intent = intent_type
                break
        
        return {"intent": intent, "entities": entities}
    
    def generate_sql_with_intelligence(self, query: str, schema: Dict[str, Any]) -> str:
        """Generate SQL using intelligent natural language processing"""
        query_lower = query.lower()
        
        # Parse the query to understand intent and entities
        parsed = self.parse_natural_language(query_lower, schema)
        
        # Build SQL dynamically based on parsed components
        return self.build_dynamic_sql(parsed, schema)
    
    def parse_natural_language(self, query: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Parse natural language query into structured components"""
        parsed = {
            "action": "select",  # select, count, sum, avg, etc.
            "tables": [],
            "columns": [],
            "conditions": [],
            "groupby": [],
            "orderby": [],
            "limit": None,
            "joins": [],
            "cross_table_query": False
        }
        
        # Detect action/intent
        if any(word in query for word in ["count", "how many", "number of"]):
            parsed["action"] = "count"
        elif any(word in query for word in ["total", "sum", "sales", "revenue", "sold"]):
            parsed["action"] = "sum"
        elif any(word in query for word in ["average", "avg"]):
            parsed["action"] = "avg"
        elif any(word in query for word in ["maximum", "max", "highest", "most expensive"]):
            parsed["action"] = "max"
        elif any(word in query for word in ["minimum", "min", "lowest", "cheapest"]):
            parsed["action"] = "min"
        
        # Detect all entities mentioned in the query
        mentioned_entities = []
        table_keywords = {
            "users": ["user", "customer", "people", "person", "client"],
            "products": ["product", "item", "goods", "merchandise", "catalog"],
            "orders": ["order", "purchase", "transaction", "sale"],
            "order_items": ["order item", "purchased item", "line item"]
        }
        
        for table, keywords in table_keywords.items():
            if any(keyword in query for keyword in keywords):
                mentioned_entities.append(table)
        
        # Detect cross-table queries
        has_price_condition = any(word in query for word in ["price", "cost", "expensive", "cheap", "$"])
        has_user_entity = any(entity in mentioned_entities for entity in ["users"])
        has_product_entity = any(entity in mentioned_entities for entity in ["products"])
        has_order_entity = any(entity in mentioned_entities for entity in ["orders"])
        
        # Check for purchase/buying relationships
        has_purchase_relationship = any(word in query for word in ["bought", "purchased", "ordered", "buy"])
        
        # Check for sales/revenue queries with category filters
        has_sales_revenue = any(word in query for word in ["sales", "revenue", "sold", "selling"])
        has_category_mention = any(word in query for word in ["book", "books", "electronics", "kitchen", "furniture", "category"])
        
        # Determine if this is a cross-table query
        if (has_user_entity and (has_price_condition or has_purchase_relationship)) or \
           (has_user_entity and has_product_entity) or \
           (has_user_entity and has_order_entity and has_price_condition) or \
           (has_sales_revenue and has_category_mention) or \
           (has_order_entity and has_category_mention):
            parsed["cross_table_query"] = True
            parsed["tables"] = ["users", "orders", "order_items", "products"]  # Full join chain
        elif has_order_entity and has_price_condition:
            parsed["cross_table_query"] = True
            parsed["tables"] = ["orders", "order_items", "products"]
        else:
            # Single table query
            if mentioned_entities:
                parsed["tables"] = [mentioned_entities[0]]
            elif has_price_condition or has_category_mention:
                parsed["tables"] = ["products"]
            elif any(word in query for word in ["revenue", "total amount", "sales"]):
                parsed["tables"] = ["orders"]
            else:
                parsed["tables"] = ["products"]  # default
        
        # Extract conditions based on query type
        self._extract_category_filters(query, parsed)
        self._extract_status_filters(query, parsed)
        self._extract_price_filters(query, parsed)
        self._extract_name_filters(query, parsed)
        
        # Detect grouping
        if "by category" in query or "category" in query and parsed["action"] == "count":
            parsed["groupby"].append("p.category" if parsed["cross_table_query"] else "category")
        elif "by city" in query or ("city" in query and "user" in query):
            parsed["groupby"].append("u.city" if parsed["cross_table_query"] else "city")
        elif "by status" in query:
            parsed["groupby"].append("o.status" if parsed["cross_table_query"] else "status")
        
        # Detect sorting
        if any(word in query for word in ["recent", "latest", "newest"]):
            if "orders" in parsed["tables"]:
                parsed["orderby"].append(("o.order_date", "DESC"))
            else:
                parsed["orderby"].append(("created_at", "DESC"))
        elif any(word in query for word in ["expensive", "highest price", "most expensive"]):
            parsed["orderby"].append(("p.price", "DESC") if parsed["cross_table_query"] else ("price", "DESC"))
        elif any(word in query for word in ["cheapest", "lowest price", "least expensive"]):
            parsed["orderby"].append(("p.price", "ASC") if parsed["cross_table_query"] else ("price", "ASC"))
        elif "best selling" in query or "popular" in query:
            parsed["action"] = "bestselling"
        
        # Detect limits
        if any(word in query for word in ["top 5", "first 5"]):
            parsed["limit"] = 5
        elif any(word in query for word in ["top 10", "first 10"]):
            parsed["limit"] = 10
        elif not any(word in query for word in ["all", "every"]):
            parsed["limit"] = 10  # default limit
        
        return parsed
    
    def build_dynamic_sql(self, parsed: Dict[str, Any], schema: Dict[str, Any]) -> str:
        """Build SQL query from parsed components"""
        
        # Handle special cases first
        if parsed["action"] == "bestselling":
            return """
            SELECT p.name, p.category, SUM(oi.quantity) as total_sold 
            FROM products p 
            JOIN order_items oi ON p.id = oi.product_id 
            GROUP BY p.id, p.name, p.category 
            ORDER BY total_sold DESC 
            LIMIT 5;
            """
        
        # Handle cross-table queries (users who bought products with conditions)
        if parsed["cross_table_query"]:
            return self._build_cross_table_sql(parsed)
        
        # Single table queries
        primary_table = parsed["tables"][0] if parsed["tables"] else "products"
        
        # Build SELECT clause
        if parsed["action"] == "count":
            if parsed["groupby"]:
                select_clause = f"SELECT {parsed['groupby'][0]}, COUNT(*) as count"
            else:
                select_clause = "SELECT COUNT(*) as count"
        elif parsed["action"] == "sum":
            if "orders" in parsed["tables"]:
                select_clause = "SELECT SUM(total_amount) as total_revenue"
            else:
                select_clause = "SELECT SUM(price) as total_price"
        elif parsed["action"] == "avg":
            select_clause = "SELECT AVG(price) as average_price"
        elif parsed["action"] in ["max", "min"]:
            select_clause = "SELECT *"
        else:
            # Need to join with users for order queries to get user names
            if primary_table == "orders":
                select_clause = "SELECT o.*, u.name as user_name"
                parsed["joins"].append(("users", "u", "o.user_id = u.id"))
            else:
                select_clause = "SELECT *"
        
        # Build FROM clause
        if parsed["joins"]:
            from_clause = f"FROM {primary_table} o"
            for join_table, alias, condition in parsed["joins"]:
                from_clause += f" JOIN {join_table} {alias} ON {condition}"
        else:
            from_clause = f"FROM {primary_table}"
        
        # Build WHERE clause
        where_conditions = []
        for column, operator, value in parsed["conditions"]:
            if operator.upper() == "LIKE":
                where_conditions.append(f"{column} {operator} '{value}'")
            elif isinstance(value, str):
                where_conditions.append(f"{column} {operator} '{value}'")
            else:
                where_conditions.append(f"{column} {operator} {value}")
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Build GROUP BY clause
        groupby_clause = ""
        if parsed["groupby"]:
            groupby_clause = f"GROUP BY {', '.join(parsed['groupby'])}"
        
        # Build ORDER BY clause
        orderby_clause = ""
        if parsed["orderby"]:
            order_parts = []
            for column, direction in parsed["orderby"]:
                order_parts.append(f"{column} {direction}")
            orderby_clause = f"ORDER BY {', '.join(order_parts)}"
        
        # Build LIMIT clause
        limit_clause = ""
        if parsed["limit"]:
            limit_clause = f"LIMIT {parsed['limit']}"
        
        # Combine all parts
        sql_parts = [select_clause, from_clause]
        if where_clause:
            sql_parts.append(where_clause)
        if groupby_clause:
            sql_parts.append(groupby_clause)
        if orderby_clause:
            sql_parts.append(orderby_clause)
        if limit_clause:
            sql_parts.append(limit_clause)
        
        return " ".join(sql_parts) + ";"
    
    def _build_cross_table_sql(self, parsed: Dict[str, Any]) -> str:
        """Build SQL for cross-table queries (e.g., users who bought expensive products, sales data)"""
        
        # First, determine what type of query this is
        is_sales_query = parsed["action"] == "sum"
        is_count_query = parsed["action"] == "count"
        
        # Build the base join structure
        if is_sales_query or is_count_query:
            # For aggregation queries, we need the full join chain
            from_clause = """FROM orders o 
            JOIN order_items oi ON o.id = oi.order_id 
            JOIN products p ON oi.product_id = p.id"""
            
            if is_sales_query:
                # Sales queries: return total revenue
                select_clause = "SELECT SUM(oi.quantity * oi.price) as total_sales"
            else:
                # Count queries with grouping
                if parsed["groupby"]:
                    # If we have a groupby, we might need users joined
                    if "city" in parsed["groupby"][0]:
                        from_clause = """FROM users u 
                        JOIN orders o ON u.id = o.user_id 
                        JOIN order_items oi ON o.id = oi.order_id 
                        JOIN products p ON oi.product_id = p.id"""
                        select_clause = f"SELECT {parsed['groupby'][0]}, COUNT(DISTINCT u.id) as count"
                    else:
                        select_clause = f"SELECT {parsed['groupby'][0]}, COUNT(*) as count"
                else:
                    select_clause = "SELECT COUNT(*) as count"
        else:
            # Non-aggregation queries: show detailed results
            from_clause = """FROM users u 
            JOIN orders o ON u.id = o.user_id 
            JOIN order_items oi ON o.id = oi.order_id 
            JOIN products p ON oi.product_id = p.id"""
            select_clause = "SELECT DISTINCT u.*, p.name as product_name, p.price as product_price, p.category as product_category"
        
        # Build WHERE clause with proper table prefixes
        where_conditions = []
        for column, operator, value in parsed["conditions"]:
            # Map column names to correct table aliases
            if column == "price":
                column = "p.price"
            elif column == "category":
                column = "p.category"
            elif column == "status":
                column = "o.status"
            elif column == "name" and any("product" in str(cond) for cond in parsed["conditions"]):
                column = "p.name"
            elif column == "name":
                column = "u.name" if "u" in from_clause else "p.name"
            elif column == "city":
                column = "u.city"
            
            if operator.upper() == "LIKE":
                where_conditions.append(f"{column} {operator} '{value}'")
            elif isinstance(value, str):
                where_conditions.append(f"{column} {operator} '{value}'")
            else:
                where_conditions.append(f"{column} {operator} {value}")
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Build GROUP BY clause
        groupby_clause = ""
        if parsed["groupby"]:
            groupby_clause = f"GROUP BY {', '.join(parsed['groupby'])}"
        
        # Build ORDER BY clause
        orderby_clause = ""
        if parsed["orderby"]:
            order_parts = []
            for column, direction in parsed["orderby"]:
                order_parts.append(f"{column} {direction}")
            orderby_clause = f"ORDER BY {', '.join(order_parts)}"
        
        # Build LIMIT clause (not for aggregation queries)
        limit_clause = ""
        if parsed["limit"] and not (is_sales_query or is_count_query):
            limit_clause = f"LIMIT {parsed['limit']}"
        
        # Combine all parts
        sql_parts = [select_clause, from_clause]
        if where_clause:
            sql_parts.append(where_clause)
        if groupby_clause:
            sql_parts.append(groupby_clause)
        if orderby_clause:
            sql_parts.append(orderby_clause)
        if limit_clause:
            sql_parts.append(limit_clause)
        
        return " ".join(sql_parts) + ";"
    
    def _extract_category_filters(self, query: str, parsed: Dict[str, Any]) -> None:
        """Extract category-based filters from the query"""
        categories = {
            "Books": ["book", "books", "literature", "reading", "novel", "textbook"],
            "Electronics": ["electronics", "electronic", "tech", "gadget", "device"],
            "Kitchen": ["kitchen", "cooking", "cookware", "utensil"],
            "Furniture": ["furniture", "chair", "table", "desk", "sofa"],
            "Clothing": ["clothing", "clothes", "apparel", "fashion"],
            "Sports": ["sports", "sport", "fitness", "exercise"],
            "Home": ["home", "household", "domestic"],
            "Toys": ["toy", "toys", "games", "play"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in query for keyword in keywords):
                parsed["conditions"].append(("category", "=", category))
                break
    
    def _extract_status_filters(self, query: str, parsed: Dict[str, Any]) -> None:
        """Extract status-based filters from the query"""
        if any(word in query for word in ["pending", "waiting", "processing"]):
            parsed["conditions"].append(("status", "=", "pending"))
        elif any(word in query for word in ["completed", "finished", "done", "delivered"]):
            parsed["conditions"].append(("status", "=", "completed"))
        elif any(word in query for word in ["cancelled", "canceled", "rejected"]):
            parsed["conditions"].append(("status", "=", "cancelled"))
    
    def _extract_price_filters(self, query: str, parsed: Dict[str, Any]) -> None:
        """Extract price-based filters from the query"""
        import re
        
        # Look for price ranges like "under $50", "over $100", "between $20 and $50"
        price_patterns = [
            (r"under \$?(\d+)", lambda x: ("price", "<", float(x))),
            (r"below \$?(\d+)", lambda x: ("price", "<", float(x))),
            (r"less than \$?(\d+)", lambda x: ("price", "<", float(x))),
            (r"over \$?(\d+)", lambda x: ("price", ">", float(x))),
            (r"above \$?(\d+)", lambda x: ("price", ">", float(x))),
            (r"more than \$?(\d+)", lambda x: ("price", ">", float(x))),
            (r"exactly \$?(\d+)", lambda x: ("price", "=", float(x))),
            (r"\$(\d+)\+", lambda x: ("price", ">", float(x))),  # $500+
            (r"costs? \$?(\d+)", lambda x: ("price", "=", float(x))),
            (r"priced? at \$?(\d+)", lambda x: ("price", "=", float(x))),
        ]
        
        for pattern, condition_func in price_patterns:
            match = re.search(pattern, query)
            if match:
                parsed["conditions"].append(condition_func(match.group(1)))
                break
        
        # Handle ranges like "between $20 and $50"
        range_match = re.search(r"between \$?(\d+) and \$?(\d+)", query)
        if range_match:
            min_price, max_price = float(range_match.group(1)), float(range_match.group(2))
            parsed["conditions"].append(("price", ">=", min_price))
            parsed["conditions"].append(("price", "<=", max_price))
    
    def _extract_name_filters(self, query: str, parsed: Dict[str, Any]) -> None:
        """Extract name-based filters for searching specific items"""
        # Look for quoted strings or specific product names
        import re
        
        # Match quoted strings
        quoted_matches = re.findall(r'"([^"]+)"', query)
        for match in quoted_matches:
            parsed["conditions"].append(("name", "LIKE", f"%{match}%"))
        
        # Match single quoted strings
        single_quoted_matches = re.findall(r"'([^']+)'", query)
        for match in single_quoted_matches:
            parsed["conditions"].append(("name", "LIKE", f"%{match}%"))
        
        # Look for patterns like "named X" or "called X"
        name_patterns = [
            r"named ([a-zA-Z\s]+)",
            r"called ([a-zA-Z\s]+)",
            r"with name ([a-zA-Z\s]+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query)
            if match:
                name = match.group(1).strip()
                if len(name) > 2:  # Avoid single characters
                    parsed["conditions"].append(("name", "LIKE", f"%{name}%"))
                break
    
    def generate_sql_with_llm(self, query: str, schema: Dict[str, Any]) -> str:
        """Generate SQL using LLM (fallback to intelligent parsing if model not available)"""
        if not self.sql_generator:
            return self.generate_sql_with_intelligence(query, schema)
        
        try:
            # Create prompt for SQL generation
            schema_str = json.dumps(schema, indent=2)
            prompt = f"""
            Convert the following natural language query to SQL:
            
            Database Schema:
            {schema_str}
            
            Natural Language Query: {query}
            
            SQL Query:
            """
            
            # Generate SQL using the model
            result = self.sql_generator(
                prompt,
                max_length=200,
                num_return_sequences=1,
                temperature=0.3,
                do_sample=True
            )
            
            generated_sql = result[0]['generated_text']
            
            # Clean up the generated SQL
            sql_match = re.search(r'SELECT.*?;', generated_sql, re.IGNORECASE | re.DOTALL)
            if sql_match:
                return sql_match.group().strip()
            else:
                # Fallback to intelligent parsing approach
                return self.generate_sql_with_intelligence(query, schema)
                
        except Exception as e:
            print(f"Error generating SQL with LLM: {e}")
            return self.generate_sql_with_intelligence(query, schema)
    
    def process_natural_language_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Process natural language query and return results"""
        try:
            # Get database schema
            schema = get_database_schema(db)
            
            # Generate SQL query
            sql_query = self.generate_sql_with_llm(query, schema)
            
            # Execute the query
            results = execute_sql_query(db, sql_query)
            
            # Generate explanation
            explanation = self.generate_explanation(query, sql_query, results)
            
            return {
                "natural_query": query,
                "sql_query": sql_query,
                "results": results,
                "explanation": explanation,
                "success": True
            }
            
        except Exception as e:
            return {
                "natural_query": query,
                "sql_query": "",
                "results": [],
                "explanation": f"Error processing query: {str(e)}",
                "success": False
            }
    
    def generate_explanation(self, natural_query: str, sql_query: str, results: List[Dict]) -> str:
        """Generate intelligent human-readable explanation of the query results"""
        if not results:
            return "No results found for your query."
        
        if isinstance(results[0], dict) and "error" in results[0]:
            return f"There was an error executing the query: {results[0]['error']}"
        
        result_count = len(results)
        query_lower = natural_query.lower()
        
        # Parse the query to understand what the user was asking for
        parsed = self.parse_natural_language(query_lower, {})
        
        # Handle cross-table query explanations
        if parsed.get("cross_table_query", False):
            # Check if this is a sales/revenue query
            is_sales_query = parsed["action"] == "sum"
            
            if is_sales_query and results and "total_sales" in results[0]:
                total_sales = results[0]["total_sales"]
                if total_sales is None:
                    return "No sales found for the specified criteria."
                
                # Find category if specified
                category_condition = next((condition for condition in parsed["conditions"] if condition[0] == "category"), None)
                if category_condition:
                    category = category_condition[2]
                    return f"Total sales for {category} products: ${total_sales:,.2f}"
                else:
                    return f"Total sales: ${total_sales:,.2f}"
            elif parsed["action"] == "count":
                if results and "count" in results[0]:
                    count_value = results[0]['count']
                    if any(condition for condition in parsed["conditions"] if condition[0] == "price"):
                        price_condition = next(condition for condition in parsed["conditions"] if condition[0] == "price")
                        operator_text = {">": "over", "<": "under", ">=": "at least", "<=": "up to", "=": "exactly"}
                        op_text = operator_text.get(price_condition[1], "")
                        return f"Found {count_value} users who bought products {op_text} ${price_condition[2]}."
                    else:
                        return f"Found {count_value} users who match your criteria."
            else:
                if any(condition for condition in parsed["conditions"] if condition[0] == "price"):
                    price_condition = next(condition for condition in parsed["conditions"] if condition[0] == "price")
                    operator_text = {">": "over", "<": "under", ">=": "at least", "<=": "up to", "=": "exactly"}
                    op_text = operator_text.get(price_condition[1], "")
                    return f"Here are {result_count} users who bought products {op_text} ${price_condition[2]}."
                else:
                    return f"Here are {result_count} users who match your purchasing criteria."
        
        # Generate contextual explanations based on parsed intent
        if parsed["action"] == "count":
            if results and "count" in results[0]:
                count_value = results[0]['count']
                if "product" in query_lower:
                    if parsed["groupby"]:
                        return f"Found {result_count} product categories with a total of {count_value} products."
                    else:
                        return f"There are {count_value} products in the catalog."
                elif "user" in query_lower:
                    return f"There are {count_value} users in the system."
                elif "order" in query_lower:
                    return f"There are {count_value} orders in the database."
                else:
                    return f"Found {count_value} records matching your criteria."
        
        elif parsed["action"] == "sum":
            if results and "total_revenue" in results[0]:
                revenue = results[0]['total_revenue']
                return f"The total revenue is ${revenue:,.2f}."
            elif results and "total_price" in results[0]:
                total = results[0]['total_price']
                return f"The total price sum is ${total:,.2f}."
        
        elif parsed["action"] == "avg":
            if results and "average_price" in results[0]:
                avg = results[0]['average_price']
                return f"The average price is ${avg:,.2f}."
        
        elif parsed["action"] == "bestselling":
            return f"Here are the top {result_count} best-selling products with their sales quantities."
        
        else:
            # Regular select queries - provide contextual explanations
            if "products" in parsed["tables"]:
                if any(condition for condition in parsed["conditions"] if condition[0] == "category"):
                    category = next(condition[2] for condition in parsed["conditions"] if condition[0] == "category")
                    return f"Found {result_count} products in the {category} category."
                elif any(word in query_lower for word in ["expensive", "highest", "most expensive"]):
                    return f"Here are the {result_count} most expensive products."
                elif any(word in query_lower for word in ["cheap", "lowest", "least expensive"]):
                    return f"Here are the {result_count} cheapest products."
                elif any(word in query_lower for word in ["all", "available", "catalog"]):
                    return f"Here are all {result_count} products available in the catalog."
                else:
                    return f"Found {result_count} products matching your query."
            
            elif "users" in parsed["tables"]:
                if parsed["groupby"] and "city" in parsed["groupby"]:
                    return f"Found users across {result_count} different cities."
                else:
                    return f"Here are {result_count} users from the system."
            
            elif "orders" in parsed["tables"]:
                if any(condition for condition in parsed["conditions"] if condition[0] == "status"):
                    status = next(condition[2] for condition in parsed["conditions"] if condition[0] == "status")
                    return f"Found {result_count} {status} orders."
                elif any(word in query_lower for word in ["recent", "latest"]):
                    return f"Here are the {result_count} most recent orders."
                else:
                    return f"Found {result_count} orders in the system."
            
            else:
                return f"Found {result_count} records matching your query."

# Global instance
llm_service = LLMService() 