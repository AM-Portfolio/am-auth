package com.am.reporting.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final Logger logger = LoggerFactory.getLogger(JwtAuthenticationFilter.class);

    @Value("${app.jwt.secret:your-secret-key-here-change-in-production}")
    private String jwtSecret;

    @Value("${app.internal.jwt.secret:internal-service-super-secret-key-32chars-minimum-change-in-prod}")
    private String internalJwtSecret;

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request, @NonNull HttpServletResponse response, 
                                  @NonNull FilterChain filterChain) throws ServletException, IOException {
        
        String path = request.getServletPath();
        
        // Skip authentication for health endpoint
        if ("/health".equals(path)) {
            filterChain.doFilter(request, response);
            return;
        }

        String authHeader = request.getHeader("Authorization");
        
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            logger.warn("Missing or invalid Authorization header for path: {}", path);
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("{\"error\": \"Missing or invalid Authorization header\"}");
            return;
        }

        String token = authHeader.substring(7);
        
        try {
            DecodedJWT decodedJWT = verifyToken(token);
            
            if (decodedJWT != null) {
                String tokenType = decodedJWT.getClaim("type").asString();
                
                List<SimpleGrantedAuthority> authorities = new ArrayList<>();
                
                if ("user_token".equals(tokenType)) {
                    String userId = decodedJWT.getClaim("user_id").asString();
                    String username = decodedJWT.getClaim("username").asString();
                    authorities.add(new SimpleGrantedAuthority("ROLE_USER"));
                    
                    // Store user info in security context
                    UsernamePasswordAuthenticationToken authentication = 
                        new UsernamePasswordAuthenticationToken(username, null, authorities);
                    authentication.setDetails(Map.of(
                        "user_id", userId,
                        "username", username,
                        "token_type", "user"
                    ));
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                    
                    logger.info("User token validated for user: {}", username);
                    
                } else if ("service_token".equals(tokenType)) {
                    String serviceId = decodedJWT.getClaim("service_id").asString();
                    authorities.add(new SimpleGrantedAuthority("ROLE_SERVICE"));
                    
                    UsernamePasswordAuthenticationToken authentication = 
                        new UsernamePasswordAuthenticationToken(serviceId, null, authorities);
                    authentication.setDetails(Map.of(
                        "service_id", serviceId,
                        "token_type", "service"
                    ));
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                    
                    logger.info("Service token validated for service: {}", serviceId);
                }
                
                filterChain.doFilter(request, response);
            } else {
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.getWriter().write("{\"error\": \"Invalid token\"}");
            }
            
        } catch (Exception e) {
            logger.error("Token validation error: {}", e.getMessage());
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("{\"error\": \"Token validation failed\"}");
        }
    }

    private DecodedJWT verifyToken(String token) {
        try {
            // Try user token first
            Algorithm userAlgorithm = Algorithm.HMAC256(jwtSecret);
            JWTVerifier userVerifier = JWT.require(userAlgorithm).build();
            DecodedJWT decodedJWT = userVerifier.verify(token);
            
            if ("user_token".equals(decodedJWT.getClaim("type").asString())) {
                return decodedJWT;
            }
        } catch (JWTVerificationException e) {
            logger.debug("User token verification failed, trying service token");
        }
        
        try {
            // Try service token
            Algorithm serviceAlgorithm = Algorithm.HMAC256(internalJwtSecret);
            JWTVerifier serviceVerifier = JWT.require(serviceAlgorithm).build();
            DecodedJWT decodedJWT = serviceVerifier.verify(token);
            
            if ("service_token".equals(decodedJWT.getClaim("type").asString())) {
                return decodedJWT;
            }
        } catch (JWTVerificationException e) {
            logger.debug("Service token verification failed");
        }
        
        return null;
    }
}