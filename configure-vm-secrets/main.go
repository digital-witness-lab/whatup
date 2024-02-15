package main

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path"
	"strings"
	"time"

	secretmanager "cloud.google.com/go/secretmanager/apiv1"
	"cloud.google.com/go/secretmanager/apiv1/secretmanagerpb"
)

const envFile = "/tmp/whatup/.env"

var httpClient *http.Client

// Run initialization on package init.
func init() {
	httpClient = &http.Client{
		Timeout: time.Duration(20) * time.Second,
	}
}

func getMetadata(ctx context.Context, url string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Add("Metadata-Flavor", "Google")

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request to %s failed: %v", url, err)
	}

	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %v", err)
	}

	return body, nil
}

func getProjectID(ctx context.Context) string {
	body, err := getMetadata(ctx, "http://metadata.google.internal/computeMetadata/v1/project/project-id")
	if err != nil {
		panic(err)
	}

	return string(body)
}

// accessSecretVersion accesses the payload for the given secret version if one
// exists. The version can be a version number as a string (e.g. "5") or an
// alias (e.g. "latest").
func accessSecretVersion(ctx context.Context, name string) (string, error) {
	client, err := secretmanager.NewClient(ctx)
	if err != nil {
		return "", fmt.Errorf("failed to create secretmanager client: %w", err)
	}
	defer client.Close()

	req := &secretmanagerpb.AccessSecretVersionRequest{
		Name: name,
	}

	result, err := client.AccessSecretVersion(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to access secret version: %w", err)
	}

	return string(result.Payload.Data), nil
}

// isGoogleComputeEngineEnv returns true when executed inside a
// Google Compute Engine instance with the metadata service
// enabled.
// https://cloud.google.com/compute/docs/instances/detect-compute-engine#use_the_metadata_server_to_detect_if_a_vm_is_running_in
func isGoogleComputeEngineEnv() bool {
	resp, err := httpClient.Get("http://metadata.google.internal")
	if err != nil {
		switch ty := err.(type) {
		case *url.Error:
			// If the error is due to a timeout,
			// it more than likely is because
			// the metadata service is not
			// available.
			if ty.Timeout() {
				fmt.Println("Request to internal metadata service timed-out")
				return false
			}

			panic(err)
		default:
			panic(err)
		}
	}

	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		fmt.Println("Request to internal metadata service failed with status: " + resp.Status)
		return false
	}

	return resp.Header.Get("Metadata-Flavor") == "Google"
}

func main() {
	ctx := context.Background()

	if !isGoogleComputeEngineEnv() {
		fmt.Println("Exiting. Not running inside a Google Compute Engine env.")
		os.Exit(0)
	}

	projectID := getProjectID(ctx)
	secretRefPrefix := fmt.Sprintf("projects/%s/secrets", projectID)

	attributes_resp_body, err := getMetadata(ctx, "http://metadata.google.internal/computeMetadata/v1/instance/attributes/")
	if err != nil {
		panic(fmt.Errorf("failed to list instance attributes: %v", err))
	}

	attributes := strings.Split(string(attributes_resp_body), "\n")

	secrets := make(map[string]string)

	for _, attr := range attributes {
		url := fmt.Sprintf("http://metadata.google.internal/computeMetadata/v1/instance/attributes/%s", attr)
		attr_value_body, err := getMetadata(ctx, url)
		if err != nil {
			panic(fmt.Errorf("failed to retrieve metadata value for %s: %v", attr, err))
		}

		secretRef := strings.Trim(string(attr_value_body), " ")

		// If the value of the attribute is not a reference to a secret
		if !strings.HasPrefix(secretRef, secretRefPrefix) {
			continue
		}

		secretValue, err := accessSecretVersion(ctx, secretRef)
		if err != nil {
			panic(fmt.Errorf("failed to fetch secret %s: %v", secretRef, err))
		}

		secrets[attr] = secretValue
	}

	os.MkdirAll(path.Dir(envFile), 0755)
	f, err := os.Create(envFile)

	defer func() {
		f.Sync()
		// Ignore file close errors.
		f.Close()
	}()

	if err != nil {
		panic(fmt.Errorf("creating file %s: %v", envFile, err))
	}

	for k, v := range secrets {
		if strings.HasSuffix(k, "PEM") {
			err := writeCertFile(ctx, k, v)
			if err != nil {
				panic(fmt.Errorf("error writing secret %s to its own file: %v", k, err))
			}

			continue
		}

		_, err := f.WriteString(fmt.Sprintf("%s=%s\n", k, v))
		if err != nil {
			panic(fmt.Errorf("failed to write secret to env file: %v", err))
		}
	}

	fmt.Printf("Wrote env file %s!\n", envFile)
}

func writeCertFile(ctx context.Context, name, value string) error {
	p := path.Join("/", "run", "secrets")
	os.MkdirAll(p, 0755)

	fileName := "ssl-cert"
	if strings.Contains(name, "KEY") {
		fileName = "ssl-key"
	}
	err := os.WriteFile(path.Join(p, fileName), []byte(value), 0600)
	return err
}
