# Build context: this directory (services/ai-gateway).
#   docker build -t erh-ai-gateway services/ai-gateway
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/ai-gateway ./...

FROM gcr.io/distroless/static-debian12
COPY --from=build /out/ai-gateway /ai-gateway
EXPOSE 8080
ENTRYPOINT ["/ai-gateway"]
